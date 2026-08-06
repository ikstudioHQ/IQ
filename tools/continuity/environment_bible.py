"""
tools/continuity/environment_bible.py

Loader for continuity/environment_bible/<location_id>.json. Mirrors
CameraBible's read-only, lazy-load pattern for consistency across the
codebase.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class EnvironmentBibleRepo:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self._dir = self.root / "continuity" / "environment_bible"
        self._cache: dict[str, dict] = {}

    def get(self, location_id: str) -> Optional[dict]:
        if location_id not in self._cache:
            path = self._dir / f"{location_id}.json"
            self._cache[location_id] = (
                json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
            )
        return self._cache[location_id]

    def default_lighting(self, location_id: str) -> dict:
        bible = self.get(location_id) or {}
        return bible.get("lighting_default", {})

    def continuity_notes(self, location_id: str) -> Optional[str]:
        bible = self.get(location_id) or {}
        return bible.get("continuity_notes")
