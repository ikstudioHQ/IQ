#!/usr/bin/env python3
"""
tools/continuity/rebuild_clip_state_index.py

Rebuilds runtime/clip_state_index.sqlite from the JSON files under
continuity/clip_state/. The index is entirely derived/disposable --
continuity/clip_state/*.json remains the only source of truth. This
script can be re-run any time (e.g. after a batch generation run) to
keep the index current; it always drops and rebuilds rather than
patching, so it can never drift out of sync with the JSON files.

Why this exists: a 30-episode season at ~75 clips/episode is ~2,250
clip files. Scanning the directory tree for "the previous clip in this
thread" on every request doesn't scale; the index makes that an
indexed lookup instead.

Usage:
    python3 tools/continuity/rebuild_clip_state_index.py [repo_root]
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT_DEFAULT = Path(__file__).resolve().parents[2]

SCHEMA = """
CREATE TABLE clip_state (
    episode_id TEXT NOT NULL,
    scene_id TEXT NOT NULL,
    clip_id TEXT NOT NULL,
    sequence_index INTEGER,
    continuity_thread_id TEXT,
    previous_clip_id TEXT,
    location_id TEXT,
    qa_status TEXT,
    lifecycle_status TEXT,
    provider TEXT,
    created_at TEXT,
    PRIMARY KEY (episode_id, scene_id, clip_id)
);
CREATE INDEX idx_thread ON clip_state (continuity_thread_id, sequence_index);
CREATE INDEX idx_qa_status ON clip_state (qa_status);
CREATE INDEX idx_location ON clip_state (location_id, created_at);
"""


def rebuild(root: Path) -> int:
    clip_state_dir = root / "continuity" / "clip_state"
    index_path = root / "runtime" / "clip_state_index.sqlite"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    if index_path.exists():
        index_path.unlink()

    conn = sqlite3.connect(index_path)
    conn.executescript(SCHEMA)

    count = 0
    if clip_state_dir.exists():
        for clip_file in clip_state_dir.glob("*/*/*.json"):
            data = json.loads(clip_file.read_text(encoding="utf-8"))
            conn.execute(
                "INSERT OR REPLACE INTO clip_state "
                "(episode_id, scene_id, clip_id, sequence_index, continuity_thread_id, "
                " previous_clip_id, location_id, qa_status, lifecycle_status, provider, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    data.get("episode_id"),
                    data.get("scene_id"),
                    data.get("clip_id"),
                    data.get("sequence_index"),
                    data.get("continuity_thread_id"),
                    data.get("previous_clip_id"),
                    (data.get("environment") or {}).get("location_id"),
                    data.get("qa_status"),
                    data.get("lifecycle_status"),
                    data.get("provider"),
                    data.get("created_at"),
                ),
            )
            count += 1
    conn.commit()
    conn.close()
    return count


def main(argv=None):
    root = Path(argv[0]).resolve() if argv else ROOT_DEFAULT
    n = rebuild(root)
    print(f"Rebuilt runtime/clip_state_index.sqlite from {n} clip_state files.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
