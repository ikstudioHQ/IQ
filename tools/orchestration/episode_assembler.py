"""
tools/orchestration/episode_assembler.py

Assembles an episode's generated clip videos, in clip order, into one
video file via ffmpeg concat. If any clip in the episode never reached
PASSED status, assembly is skipped and an explicit gap report is
written instead -- never a silently truncated or gap-papered-over
episode.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from tools.orchestration.job_state import CLIP_PASSED


def assemble_episode(root: str | Path, episode_id: str, ep_job: dict) -> dict:
    root = Path(root)
    clips = sorted(ep_job["clips"].values(), key=lambda c: (c["scene_id"], c["clip_id"]))
    missing = [f"{c['scene_id']}/{c['clip_id']} ({c['status']})" for c in clips if c["status"] != CLIP_PASSED]

    report = {
        "episode_id": episode_id,
        "clip_order": [f"{c['scene_id']}/{c['clip_id']}" for c in clips],
        "missing_clips": missing,
        "assembled": False,
        "output_path": None,
    }

    if missing:
        _write_report(root, episode_id, report)
        return report

    video_paths = [
        root / "continuity" / "generated_videos" / episode_id / c["scene_id"] / f"{c['clip_id']}.mp4"
        for c in clips
    ]
    not_found = [str(p) for p in video_paths if not p.exists()]
    if not_found:
        report["missing_clips"] = [f"video file not found: {p}" for p in not_found]
        _write_report(root, episode_id, report)
        return report

    if shutil.which("ffmpeg") is None:
        report["missing_clips"] = ["ffmpeg not available -- cannot assemble even though all clips PASSED"]
        _write_report(root, episode_id, report)
        return report

    out_dir = root / "continuity" / "assembled_episodes"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{episode_id}.mp4"
    concat_list_path = out_dir / f"{episode_id}_concat_list.txt"
    concat_list_path.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in video_paths) + "\n", encoding="utf-8"
    )
    result = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list_path), "-c", "copy", str(out_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0 or not out_path.exists():
        report["missing_clips"] = [f"ffmpeg concat failed: {result.stderr[-500:]}"]
        _write_report(root, episode_id, report)
        return report

    report["assembled"] = True
    report["output_path"] = str(out_path.relative_to(root))
    _write_report(root, episode_id, report)
    return report


def _write_report(root: Path, episode_id: str, report: dict) -> None:
    out_dir = root / "continuity" / "assembly_reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{episode_id}.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
