import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.orchestration.episode_assembler import assemble_episode


def _make_video(path: Path, color: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c={color}:s=160x120:d=1", str(path)],
        capture_output=True, check=True,
    )


def test_assembles_when_all_clips_passed(tmp_path):
    ep_id = "ep_test"
    _make_video(tmp_path / "continuity/generated_videos" / ep_id / "scene_01/clip_01.mp4", "red")
    _make_video(tmp_path / "continuity/generated_videos" / ep_id / "scene_01/clip_02.mp4", "blue")
    ep_job = {"clips": {
        "scene_01/clip_01": {"scene_id": "scene_01", "clip_id": "clip_01", "status": "PASSED"},
        "scene_01/clip_02": {"scene_id": "scene_01", "clip_id": "clip_02", "status": "PASSED"},
    }}
    report = assemble_episode(tmp_path, ep_id, ep_job)
    assert report["assembled"] is True
    out = tmp_path / report["output_path"]
    assert out.exists() and out.stat().st_size > 0


def test_incomplete_episode_not_assembled_gap_reported(tmp_path):
    ep_job = {"clips": {
        "scene_01/clip_01": {"scene_id": "scene_01", "clip_id": "clip_01", "status": "PASSED"},
        "scene_01/clip_02": {"scene_id": "scene_01", "clip_id": "clip_02", "status": "WAITING_FOR_EXTERNAL_GENERATION"},
    }}
    report = assemble_episode(tmp_path, "ep_incomplete", ep_job)
    assert report["assembled"] is False
    assert any("WAITING_FOR_EXTERNAL_GENERATION" in m for m in report["missing_clips"])
    # gap report itself must be a real file, not just an in-memory return
    report_path = tmp_path / "continuity" / "assembly_reports" / "ep_incomplete.json"
    assert report_path.exists()


def test_passed_but_video_file_missing_reported_not_crashed(tmp_path):
    ep_job = {"clips": {
        "scene_01/clip_01": {"scene_id": "scene_01", "clip_id": "clip_01", "status": "PASSED"},
    }}
    report = assemble_episode(tmp_path, "ep_ghost", ep_job)
    assert report["assembled"] is False
    assert any("not found" in m for m in report["missing_clips"])
