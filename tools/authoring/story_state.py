"""
tools/authoring/story_state.py

Story State was flagged as the biggest continuity gap early on: v2.72's
world_state.json already tracked some of this (lessons learned, ongoing
friendships) but nothing ever read it, and wiring it in was deferred
until there was a real authoring layer for it to attach to. Phase 6 is
that layer.

This is season-scoped (one StoryState per season, not per-episode) --
promises and threads are meant to persist and pay off across episodes,
which is the entire point.

Every entry is written by the AUTHOR's own structured output (see
schemas.py's EpisodeScript.story_updates), never inferred by scanning
prose after the fact -- inference from free text is unreliable and
would silently drift from what the author actually intended. If an
episode's authored output doesn't declare a promise, this system will
never invent one.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class StoryThread:
    thread_id: str
    kind: str  # "promise" | "open_thread" | "secret" | "goal" | "running_joke" | "lesson" | "conflict"
    description: str
    involved_characters: list[str]
    origin_episode_id: str
    status: str = "open"  # "open" | "resolved" | "abandoned"
    resolved_episode_id: Optional[str] = None
    resolution_note: Optional[str] = None
    callback_count: int = 0  # how many later episodes have referenced this thread


@dataclass
class EmotionalArcEntry:
    character_id: str
    episode_id: str
    note: str  # e.g. "Zayd is learning patience after losing his temper in ep 3"


@dataclass
class StoryState:
    season_id: str
    threads: list[dict] = field(default_factory=list)  # StoryThread.__dict__ entries
    emotional_arc_log: list[dict] = field(default_factory=list)  # EmotionalArcEntry.__dict__ entries
    schema_version: str = "1.0"
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    def open_threads(self, kind: Optional[str] = None) -> list[dict]:
        return [
            t for t in self.threads
            if t["status"] == "open" and (kind is None or t["kind"] == kind)
        ]

    def threads_involving(self, character_id: str, *, open_only: bool = True) -> list[dict]:
        return [
            t for t in self.threads
            if character_id in t["involved_characters"] and (not open_only or t["status"] == "open")
        ]


class StoryStateRepo:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self._dir = self.root / "continuity" / "story_state"

    def _path(self, season_id: str) -> Path:
        return self._dir / f"{season_id}.json"

    def load(self, season_id: str) -> StoryState:
        path = self._path(season_id)
        if not path.exists():
            return StoryState(season_id=season_id)
        data = json.loads(path.read_text(encoding="utf-8"))
        return StoryState(**{k: v for k, v in data.items() if k in StoryState.__dataclass_fields__})

    def save(self, state: StoryState) -> Path:
        state.updated_at = datetime.now(timezone.utc).isoformat()
        path = self._path(state.season_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return path

    def apply_episode_updates(self, season_id: str, episode_id: str, story_updates: dict) -> StoryState:
        """story_updates is the author's own structured declaration, shaped like:
        {
          "new_threads": [{"kind": "promise", "description": "...",
                            "involved_characters": ["char_002_amira"]}],
          "resolved_thread_ids": ["thread_ep03_promise_help_zayd"],
          "resolution_notes": {"thread_ep03_promise_help_zayd": "Amira kept her promise and helped Zayd fix the kite."},
          "referenced_thread_ids": ["thread_ep01_running_joke_lost_sandal"],
          "emotional_notes": [{"character_id": "char_001_zayd", "note": "..."}]
        }
        Every field is optional; missing fields mean the author declared nothing
        of that kind for this episode -- not an error.
        """
        state = self.load(season_id)
        by_id = {t["thread_id"]: t for t in state.threads}

        for new in story_updates.get("new_threads", []):
            thread_id = f"thread_{episode_id}_{new['kind']}_{len(state.threads)}"
            thread = StoryThread(
                thread_id=thread_id,
                kind=new["kind"],
                description=new["description"],
                involved_characters=new.get("involved_characters", []),
                origin_episode_id=episode_id,
            )
            state.threads.append(asdict(thread))
            by_id[thread_id] = state.threads[-1]

        for resolved_id in story_updates.get("resolved_thread_ids", []):
            if resolved_id in by_id:
                by_id[resolved_id]["status"] = "resolved"
                by_id[resolved_id]["resolved_episode_id"] = episode_id
                by_id[resolved_id]["resolution_note"] = story_updates.get("resolution_notes", {}).get(resolved_id)

        for ref_id in story_updates.get("referenced_thread_ids", []):
            if ref_id in by_id:
                by_id[ref_id]["callback_count"] += 1

        for note in story_updates.get("emotional_notes", []):
            state.emotional_arc_log.append(asdict(EmotionalArcEntry(
                character_id=note["character_id"], episode_id=episode_id, note=note["note"],
            )))

        self.save(state)
        return state
