"""
tools/orchestration/job_state.py

Persistent state for the whole season production run. One JSON file per
season (continuity/job_state/<season_id>.json), matching the repo's
existing per-entity-file convention. This IS the resume mechanism: the
orchestrator's advance() function (season_orchestrator.py) is a pure
function of this file plus the other Phase 1-6 artifacts already on
disk (clip_state, generated_requests, qa_reports, authored_episodes).
Interrupt the process at any point, call advance() again later, and it
picks up exactly where the persisted state says it left off -- no
in-memory-only state exists anywhere in this pipeline.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Clip-level states. Matches the vocabulary requested: GENERATED,
# WAITING_FOR_EXTERNAL_GENERATION, FAILED, BLOCKED, QA_REQUIRED,
# REPAIR_REQUIRED, plus the states needed before generation is even
# attempted.
CLIP_PENDING = "PENDING"
CLIP_REQUEST_BUILT = "REQUEST_BUILT"
CLIP_BLOCKED = "BLOCKED"                                  # safety/validation blocked the request itself
CLIP_WAITING_FOR_EXTERNAL_GENERATION = "WAITING_FOR_EXTERNAL_GENERATION"  # ready to send to Veo, no credential available
CLIP_GENERATED = "GENERATED"
CLIP_FAILED = "FAILED"                                     # a real generation attempt errored
CLIP_QA_REQUIRED = "QA_REQUIRED"
CLIP_REPAIR_REQUIRED = "REPAIR_REQUIRED"
CLIP_PASSED = "PASSED"

EPISODE_PENDING_AUTHORING = "PENDING_AUTHORING"
EPISODE_WAITING_FOR_EXTERNAL_AUTHORING = "WAITING_FOR_EXTERNAL_AUTHORING"
EPISODE_AUTHORED = "AUTHORED"
EPISODE_CLIPS_PLANNED = "CLIPS_PLANNED"
EPISODE_IN_PROGRESS = "IN_PROGRESS"
EPISODE_ASSEMBLED = "ASSEMBLED"
EPISODE_INCOMPLETE = "INCOMPLETE"  # some clips never got past WAITING/FAILED -- assembly skipped, not hidden
# Production-gate repair (opt-in, see season_orchestrator.py's
# run_production_gates flag): the Islamic Gate or Duration Gate
# rejected this episode after authoring, before any clip was planned.
EPISODE_GATE_REPAIR_REQUIRED = "GATE_REPAIR_REQUIRED"

SEASON_PENDING_CONCEPT = "PENDING_CONCEPT"
SEASON_WAITING_FOR_EXTERNAL_AUTHORING = "WAITING_FOR_EXTERNAL_AUTHORING"
SEASON_IN_PROGRESS = "IN_PROGRESS"
SEASON_COMPLETE = "COMPLETE"
SEASON_INCOMPLETE = "INCOMPLETE"


@dataclass
class ClipJob:
    episode_id: str
    scene_id: str
    clip_id: str
    status: str = CLIP_PENDING
    attempts: int = 0
    last_error: Optional[str] = None


@dataclass
class EpisodeJob:
    episode_id: str
    status: str = EPISODE_PENDING_AUTHORING
    clips: dict = field(default_factory=dict)  # clip_key -> ClipJob.__dict__


@dataclass
class SeasonJob:
    season_id: str
    theme: str
    episode_count: int
    episode_duration_minutes: int
    language: str
    target_age: str
    provider_id: str
    status: str = SEASON_PENDING_CONCEPT
    episodes: dict = field(default_factory=dict)  # episode_id -> EpisodeJob.__dict__
    season_acceptance: Optional[str] = None  # last Season Acceptance Gate verdict, if run
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: str = "1.0"

    def to_dict(self) -> dict:
        return asdict(self)

    def get_episode(self, episode_id: str) -> Optional[dict]:
        return self.episodes.get(episode_id)

    def ensure_episode(self, episode_id: str) -> dict:
        if episode_id not in self.episodes:
            self.episodes[episode_id] = asdict(EpisodeJob(episode_id=episode_id))
        return self.episodes[episode_id]

    def ensure_clip(self, episode_id: str, scene_id: str, clip_id: str) -> dict:
        ep = self.ensure_episode(episode_id)
        key = f"{scene_id}/{clip_id}"
        if key not in ep["clips"]:
            ep["clips"][key] = asdict(ClipJob(episode_id=episode_id, scene_id=scene_id, clip_id=clip_id))
        return ep["clips"][key]

    def all_clips(self) -> list[dict]:
        return [c for ep in self.episodes.values() for c in ep["clips"].values()]


class JobStateRepo:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self._dir = self.root / "continuity" / "job_state"

    def _path(self, season_id: str) -> Path:
        return self._dir / f"{season_id}.json"

    def exists(self, season_id: str) -> bool:
        return self._path(season_id).exists()

    def load(self, season_id: str) -> Optional[SeasonJob]:
        path = self._path(season_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return SeasonJob(**{k: v for k, v in data.items() if k in SeasonJob.__dataclass_fields__})

    def save(self, job: SeasonJob) -> Path:
        job.updated_at = datetime.now(timezone.utc).isoformat()
        path = self._path(job.season_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(job.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return path

    def create(self, *, season_id: str, theme: str, episode_count: int,
               episode_duration_minutes: int, language: str, target_age: str,
               provider_id: str) -> SeasonJob:
        """Idempotent: if a job already exists for this season_id, returns
        the EXISTING job unchanged rather than resetting it -- this is what
        makes calling generate_season() twice on the same season_id a
        resume, not a restart."""
        existing = self.load(season_id)
        if existing is not None:
            return existing
        job = SeasonJob(
            season_id=season_id, theme=theme, episode_count=episode_count,
            episode_duration_minutes=episode_duration_minutes, language=language,
            target_age=target_age, provider_id=provider_id,
        )
        self.save(job)
        return job
