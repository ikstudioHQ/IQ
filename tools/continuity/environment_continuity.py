"""
tools/continuity/environment_continuity.py

Resolves the EFFECTIVE environment state for a clip using this
precedence, highest first:

  1. Explicit override on the clip's own spec (the story deliberately
     changes something -- e.g. it's now evening).
  2. Carried forward from the most recent OTHER clip generated at the
     same location_id (across scenes/episodes, not just the immediate
     previous clip in the same scene thread -- a room doesn't reset
     between episodes just because a different scene happens between
     visits to it).
  3. The Environment Bible's default for that location.

This is the direct fix for "the pipeline should require the next clip
to begin from established state" (Phase 3 brief) rather than silently
defaulting to blank/inconsistent values when an author doesn't
re-specify every field.

Depends on runtime/clip_state_index.sqlite for "most recent clip at
this location" lookups. If the index hasn't been rebuilt since the
last batch of clips, this falls back to Environment Bible defaults
only -- it never scans the whole clip_state tree per clip (see
rebuild_clip_state_index.py's docstring for why not).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from tools.continuity.clip_state import ClipState, ClipStateRepo
from tools.continuity.environment_bible import EnvironmentBibleRepo

TRACKED_KEYS = ("time_of_day", "tone", "weather", "lighting_source")


class EnvironmentContinuityResolver:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.bible = EnvironmentBibleRepo(root)
        self.clip_state_repo = ClipStateRepo(root)
        self._index_path = self.root / "runtime" / "clip_state_index.sqlite"

    def _most_recent_clip_at_location(
        self, location_id: str, exclude_clip_id: Optional[str] = None
    ) -> Optional[ClipState]:
        if not self._index_path.exists():
            return None
        conn = sqlite3.connect(self._index_path)
        try:
            row = conn.execute(
                "SELECT episode_id, scene_id, clip_id FROM clip_state "
                "WHERE location_id = ? AND clip_id != ? "
                "ORDER BY created_at DESC LIMIT 1",
                (location_id, exclude_clip_id or ""),
            ).fetchone()
        finally:
            conn.close()
        if not row:
            return None
        return self.clip_state_repo.load(*row)

    def resolve(
        self,
        location_id: Optional[str],
        explicit_overrides: dict,
        *,
        exclude_clip_id: Optional[str] = None,
    ) -> tuple[dict, dict[str, str]]:
        """Returns (resolved_environment_dict, provenance) where provenance
        maps each resolved key to "explicit" | "carried_forward" | "bible_default"
        so the Continuity Inspector / debugging can show exactly where a
        value came from."""
        if not location_id:
            return dict(explicit_overrides), {k: "explicit" for k in explicit_overrides}

        bible_defaults = self.bible.default_lighting(location_id)
        baseline = {"time_of_day": None, "tone": None, "weather": None, "lighting_source": None}
        if bible_defaults.get("baseline"):
            baseline["time_of_day"] = "default"
            baseline["tone"] = bible_defaults["baseline"]

        previous = self._most_recent_clip_at_location(location_id, exclude_clip_id)
        carried = (previous.lighting if previous else {}) or {}

        resolved: dict = {}
        provenance: dict[str, str] = {}
        for key in TRACKED_KEYS:
            if key in explicit_overrides and explicit_overrides[key] is not None:
                resolved[key] = explicit_overrides[key]
                provenance[key] = "explicit"
            elif key in carried and carried[key] is not None:
                resolved[key] = carried[key]
                provenance[key] = "carried_forward"
            elif baseline.get(key) is not None:
                resolved[key] = baseline[key]
                provenance[key] = "bible_default"
        # any extra explicit keys not in TRACKED_KEYS pass through unchanged
        for key, value in explicit_overrides.items():
            if key not in resolved:
                resolved[key] = value
                provenance[key] = "explicit"

        return resolved, provenance

    def continuity_note_for_prompt(self, location_id: Optional[str]) -> Optional[str]:
        """Environment Bible's authored continuity_notes (e.g. 'Mirror must
        remain on east wall unless story explicitly moves it') gets folded
        into the request's negative_constraints by the Request Payload
        Builder -- this is the direct, practical fix for the exact
        cat/mirror example that started this whole project."""
        if not location_id:
            return None
        return self.bible.continuity_notes(location_id)
