#!/usr/bin/env python3
"""
tools/continuity/migrate_camera_bible.py

Derives continuity/camera_bible/camera_bible.json from the existing
phase4/engine/cinematography/camera_language.json. Same non-destructive,
idempotent pattern as migrate_v272_to_continuity.py: source file is
never touched, output is always regenerated fresh.

Unlike character/environment/prop bibles (one file per entity), the
Camera Bible is a single shared vocabulary file -- shot/lens/movement/
composition rules are looked up by scene_type, not owned by an
individual character or clip.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DEFAULT = Path(__file__).resolve().parents[2]


def migrate(root: Path, dry_run: bool = False) -> dict:
    src = root / "phase4" / "engine" / "cinematography" / "camera_language.json"
    if not src.exists():
        raise FileNotFoundError(f"{src} not found -- nothing to migrate")

    data = json.loads(src.read_text(encoding="utf-8"))
    scene_types = {s["scene_type"]: s for s in data.get("scene_types", [])}

    bible = {
        "schema_version": "1.0",
        "shot_vocabulary": sorted({s.get("camera") for s in scene_types.values() if s.get("camera")}),
        "lens_vocabulary": sorted({s.get("lens") for s in scene_types.values() if s.get("lens")}),
        "movement_vocabulary": sorted({s.get("movement") for s in scene_types.values() if s.get("movement")}),
        "composition_rules": {k: v.get("composition") for k, v in scene_types.items()},
        "scene_type_defaults": scene_types,
        "transition_rules": {
            "needs_review": True,
            "note": "Not present in source data (camera_language.json covers per-shot rules, not cut/transition rules between shots). Flagged for authoring input.",
        },
        "source_of_truth": False,
        "provenance": "migrated_from:phase4/engine/cinematography/camera_language.json",
    }

    out_path = root / "continuity" / "camera_bible" / "camera_bible.json"
    if not dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(bible, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return bible


def main(argv=None):
    root = Path(argv[0]).resolve() if argv else ROOT_DEFAULT
    bible = migrate(root)
    print(f"Camera Bible written: {len(bible['scene_type_defaults'])} scene-type defaults, "
          f"{len(bible['shot_vocabulary'])} shot types, {len(bible['movement_vocabulary'])} movement types.")
    if bible["transition_rules"].get("needs_review"):
        print("NOTE: transition_rules needs_review -- not present in source data.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
