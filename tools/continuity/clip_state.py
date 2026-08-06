"""
tools/continuity/clip_state.py

ClipState is the persistent continuity record written after every clip
is planned/generated. One JSON file per clip under
continuity/clip_state/<episode_id>/<scene_id>/<clip_id>.json -- git
diffable, human readable, matches the repo's existing per-file
convention.

ClipStateRepo provides read/write plus "previous clip in this
continuity thread" lookup, which is the actual mechanism Last Frame
Continuity (Phase 3) will depend on.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


@dataclass
class ClipState:
    episode_id: str
    scene_id: str
    clip_id: str
    sequence_index: int
    continuity_thread_id: str
    previous_clip_id: Optional[str]
    characters_present: list[str] = field(default_factory=list)
    character_positions: dict[str, str] = field(default_factory=dict)
    environment: dict[str, Any] = field(default_factory=dict)
    camera: dict[str, Any] = field(default_factory=dict)
    lighting: dict[str, Any] = field(default_factory=dict)
    props_visible: list[str] = field(default_factory=list)
    emotions: dict[str, str] = field(default_factory=dict)
    music: dict[str, Any] = field(default_factory=dict)
    prompt_text: str = ""
    reference_images_used: list[dict] = field(default_factory=list)
    previous_frame_used: Optional[str] = None
    provider: str = ""
    generation_settings: dict[str, Any] = field(default_factory=dict)
    qa_status: str = "PENDING"
    # -- Phase 3 additions (backward compatible: new fields, all optional
    # with defaults, so ClipState JSON written in Phase 2 still loads fine
    # via from_dict()'s known-field filter) --------------------------------
    # `output` is populated AFTER a clip is actually generated (by a human
    # or an external automation calling register_clip_output() -- this
    # system does not call the Veo API itself yet). It is intentionally
    # separate from `previous_frame_used` above, which records what THIS
    # clip used as ITS OWN input; `output` records what THIS clip PRODUCED,
    # which is what the NEXT clip needs to read for Last Frame Continuity.
    output: dict[str, Any] = field(default_factory=dict)
    # "REQUEST_BUILT" -> "GENERATED" (set by register_clip_output).
    # Deliberately separate from qa_status (which Phase 5 owns) so this
    # phase's bookkeeping never collides with QA's vocabulary.
    lifecycle_status: str = "REQUEST_BUILT"
    # Phase 5 addition: how many times Auto-Repair has rebuilt this exact
    # clip. Capped by qa_engine.MAX_REPAIR_ATTEMPTS to prevent an infinite
    # repair loop. New field with a default -- old ClipState JSON without
    # it still loads fine.
    repair_attempt: int = 0
    schema_version: str = "1.0"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ClipState":
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in known})


class ClipStateRepo:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.base_dir = self.root / "continuity" / "clip_state"

    def _path(self, episode_id: str, scene_id: str, clip_id: str) -> Path:
        return self.base_dir / episode_id / scene_id / f"{clip_id}.json"

    def save(self, clip_state: ClipState) -> Path:
        path = self._path(clip_state.episode_id, clip_state.scene_id, clip_state.clip_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(clip_state.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return path

    def load(self, episode_id: str, scene_id: str, clip_id: str) -> Optional[ClipState]:
        path = self._path(episode_id, scene_id, clip_id)
        if not path.exists():
            return None
        return ClipState.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def get_previous_in_thread(self, clip_state: ClipState) -> Optional[ClipState]:
        """The mechanism Last Frame Continuity depends on: given the clip
        about to be generated, find the clip immediately before it in the
        same continuity thread (same episode+scene, sequence_index - 1)."""
        if clip_state.previous_clip_id is None:
            return None
        return self.load(clip_state.episode_id, clip_state.scene_id, clip_state.previous_clip_id)

    def all_clips_for_episode(self, episode_id: str) -> list[ClipState]:
        ep_dir = self.base_dir / episode_id
        if not ep_dir.exists():
            return []
        out = []
        for scene_dir in sorted(ep_dir.iterdir()):
            if not scene_dir.is_dir():
                continue
            for clip_file in sorted(scene_dir.glob("*.json")):
                out.append(ClipState.from_dict(json.loads(clip_file.read_text(encoding="utf-8"))))
        return out
