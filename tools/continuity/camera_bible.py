"""
tools/continuity/camera_bible.py

Thin loader for continuity/camera_bible/camera_bible.json. Provides
scene-type camera defaults (shot, lens, movement, composition) so
authors don't have to specify full camera language for every clip by
hand, and so different authors/episodes don't invent inconsistent
camera vocabulary. A clip's own explicit camera spec always overrides
these defaults -- this is a fallback/consistency layer, not a lock.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class CameraBible:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self._path = self.root / "continuity" / "camera_bible" / "camera_bible.json"
        self._data: Optional[dict] = None

    def _load(self) -> dict:
        if self._data is None:
            if not self._path.exists():
                self._data = {"scene_type_defaults": {}}
            else:
                self._data = json.loads(self._path.read_text(encoding="utf-8"))
        return self._data

    def defaults_for_scene_type(self, scene_type: str) -> dict:
        return self._load().get("scene_type_defaults", {}).get(scene_type, {})

    def resolve_camera_metadata(self, scene_type: Optional[str], explicit_camera: dict) -> dict:
        """explicit_camera (from the SceneClipSpec) always wins field-by-field;
        Camera Bible only fills in gaps, and only if a scene_type was given."""
        if not scene_type:
            return dict(explicit_camera)
        defaults = self.defaults_for_scene_type(scene_type)
        resolved = {
            "shot": explicit_camera.get("shot", defaults.get("camera")),
            "lens": explicit_camera.get("lens", defaults.get("lens")),
            "movement": explicit_camera.get("movement", defaults.get("movement")),
            "composition": explicit_camera.get("composition", defaults.get("composition")),
        }
        resolved.update({k: v for k, v in explicit_camera.items() if k not in resolved})
        return resolved

    def known_scene_types(self) -> list[str]:
        return sorted(self._load().get("scene_type_defaults", {}).keys())
