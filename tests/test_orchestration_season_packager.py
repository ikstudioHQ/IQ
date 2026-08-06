import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.orchestration.season_packager import package_season


def test_package_season_produces_real_readable_zip(tmp_path):
    season_id = "ep_pkg_test"
    # Real artifacts, written directly (not via the full pipeline -- this
    # test targets the packager itself, not the whole orchestrator)
    (tmp_path / "continuity" / "story_state").mkdir(parents=True)
    (tmp_path / "continuity" / "story_state" / f"{season_id}.json").write_text('{"season_id":"ep_pkg_test"}')
    (tmp_path / "continuity" / "clip_state" / season_id / "scene_01").mkdir(parents=True)
    (tmp_path / "continuity" / "clip_state" / season_id / "scene_01" / "clip_01.json").write_text("{}")
    # A prohibited file placed right alongside real artifacts -- must be excluded
    (tmp_path / "continuity" / "clip_state" / season_id / "scene_01" / "__pycache__").mkdir()
    (tmp_path / "continuity" / "clip_state" / season_id / "scene_01" / "__pycache__" / "x.pyc").write_text("junk")

    job = {
        "season_id": season_id, "status": "COMPLETE", "episode_count": 1,
        "episodes": {season_id: {"status": "ASSEMBLED", "clips": {
            "scene_01/clip_01": {"status": "PASSED"},
        }}},
    }
    result = package_season(tmp_path, season_id, job, output_path=tmp_path / "out.zip")

    zip_path = Path(result["zip_path"])
    assert zip_path.exists()
    assert result["sha256"] == __import__("hashlib").sha256(zip_path.read_bytes()).hexdigest()

    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        assert any("story_state" in n for n in names)
        assert any("clip_01.json" in n for n in names)
        assert not any("__pycache__" in n or n.endswith(".pyc") for n in names)
        assert any("production_status" in n for n in names)
        assert any(n.startswith("continuity/manifests/") for n in names)


def test_manifest_file_count_matches_zip_membership_exactly(tmp_path):
    """Regression test for a real off-by-one found during Phase 8's
    independent artifact verification: the manifest used to undercount
    by exactly 1 because it didn't count its own file, even though the
    manifest genuinely ends up inside the zip."""
    season_id = "ep_pkg_offbyone"
    (tmp_path / "continuity" / "story_state").mkdir(parents=True)
    (tmp_path / "continuity" / "story_state" / f"{season_id}.json").write_text("{}")
    job = {"season_id": season_id, "status": "INCOMPLETE", "episode_count": 1, "episodes": {}}
    result = package_season(tmp_path, season_id, job, output_path=tmp_path / "out4.zip")

    with zipfile.ZipFile(result["zip_path"]) as z:
        actual_count = len(z.namelist())
    assert result["manifest"]["file_count"] == actual_count


def test_manifest_lists_actual_included_files(tmp_path):
    season_id = "ep_pkg_manifest"
    (tmp_path / "continuity" / "story_state").mkdir(parents=True)
    (tmp_path / "continuity" / "story_state" / f"{season_id}.json").write_text("{}")
    job = {"season_id": season_id, "status": "INCOMPLETE", "episode_count": 1, "episodes": {}}
    result = package_season(tmp_path, season_id, job, output_path=tmp_path / "out2.zip")
    assert result["manifest"]["file_count"] == len(result["manifest"]["files"])
    assert result["manifest"]["file_count"] > 0


def test_status_report_reflects_real_clip_counts(tmp_path):
    season_id = "ep_pkg_status"
    job = {
        "season_id": season_id, "status": "IN_PROGRESS", "episode_count": 1,
        "episodes": {season_id: {"status": "IN_PROGRESS", "clips": {
            "s/c1": {"status": "PASSED"}, "s/c2": {"status": "WAITING_FOR_EXTERNAL_GENERATION"},
        }}},
    }
    result = package_season(tmp_path, season_id, job, output_path=tmp_path / "out3.zip")
    report = result["status_report"]
    assert report["total_clips"] == 2
    assert report["clip_status_breakdown"]["PASSED"] == 1
    assert report["clip_status_breakdown"]["WAITING_FOR_EXTERNAL_GENERATION"] == 1
