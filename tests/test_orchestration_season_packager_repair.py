import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.authoring.manual_author_seam import register_authored_episode, register_season_concept
from tools.authoring.manual_author_seam import load_authored_episode
from tools.authoring.scene_to_clip_bridge import build_clip_specs
from tools.continuity.assembler import ContinuityAssembler
from tools.orchestration.job_state import JobStateRepo
from tools.orchestration.season_orchestrator import generate_season
from tools.orchestration.season_packager import (
    collect_referenced_registry_ids,
    package_season,
    verify_frozen_package,
)
from tools.production_gates.season_acceptance import run_season_acceptance_gate
from tools.providers.veo31_fast import Veo31FastProvider


def _build_real_season(root, season_id="pkgtest_season", episode_id="pkgtest_ep1",
                        location_id="loc_family_living_room", prop_ids=None):
    prop_ids = prop_ids or []
    episode_data = {
        "episode_id": episode_id, "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
        "scenes": [{"scene_id": "s1", "location_id": location_id,
                    "characters_present": ["char_001_zayd"], "props_visible": prop_ids,
                    "environment_overrides": {},
                    "beats": [{"beat_id": "b1", "kind": "dialogue", "character_id": "char_001_zayd",
                               "text": "A real line of dialogue for packaging tests.", "estimated_seconds": None}]}],
        "song": None, "story_updates": {},
    }
    register_season_concept(root, {
        "season_id": season_id, "theme": "t", "language": "English", "target_age": "5-8",
        "episode_count": 1, "episode_duration_minutes": 5,
        "premises": [{"episode_id": episode_id, "title": "t", "premise": "t", "arc_position": "opener"}],
    })
    register_authored_episode(root, season_id, episode_data)
    generate_season(root, season_id=season_id, theme="t", episode_count=1, episode_duration_minutes=5,
                     language="English", target_age="5-8", author_provider=None, veo_executor=None)

    episode = load_authored_episode(root, episode_id)
    provider = Veo31FastProvider()
    specs, _ = build_clip_specs(root, episode, provider.capabilities())
    assembler = ContinuityAssembler(str(root), provider)
    for spec in specs:
        assembler.process_clip(spec)

    run_season_acceptance_gate(root, season_id, [episode_id], "veo-3.1-fast", 5)
    job = JobStateRepo(root).load(season_id).to_dict()
    return season_id, episode_id, job


def test_full_real_season_packages_through_official_function_only(isolated_root):
    season_id, episode_id, job = _build_real_season(isolated_root)
    result = package_season(isolated_root, season_id, job, output_path=isolated_root / "out.zip")
    assert Path(result["zip_path"]).exists()


def test_all_five_gate_result_types_physically_in_zip(isolated_root):
    season_id, episode_id, job = _build_real_season(isolated_root)
    result = package_season(isolated_root, season_id, job, output_path=isolated_root / "out.zip")
    with zipfile.ZipFile(result["zip_path"]) as z:
        names = z.namelist()
    for gate_dir in ("duration_gate", "islamic_gate", "song_gate", "continuity_gate", "season_acceptance"):
        assert any(n.startswith(f"continuity/{gate_dir}/") for n in names), f"{gate_dir} missing from zip"


def test_referenced_character_registry_entry_physically_in_zip(isolated_root):
    season_id, episode_id, job = _build_real_season(isolated_root)
    result = package_season(isolated_root, season_id, job, output_path=isolated_root / "out.zip")
    with zipfile.ZipFile(result["zip_path"]) as z:
        names = z.namelist()
    assert "continuity/character_bible/char_001_zayd.json" in names
    assert "continuity/environment_bible/loc_family_living_room.json" in names


def test_new_season_specific_environment_and_prop_included(isolated_root):
    (isolated_root / "continuity" / "environment_bible").mkdir(parents=True, exist_ok=True)
    (isolated_root / "continuity" / "prop_registry").mkdir(parents=True, exist_ok=True)
    (isolated_root / "continuity" / "environment_bible" / "loc_brand_new_place.json").write_text(
        json.dumps({"location_id": "loc_brand_new_place", "display_name": "Brand New Place"}))
    (isolated_root / "continuity" / "prop_registry" / "prop_brand_new_thing.json").write_text(
        json.dumps({"prop_id": "prop_brand_new_thing", "display_name": "Brand New Thing"}))
    season_id, episode_id, job = _build_real_season(
        isolated_root, season_id="new_entity_season", episode_id="new_entity_ep",
        location_id="loc_brand_new_place", prop_ids=["prop_brand_new_thing"],
    )
    result = package_season(isolated_root, season_id, job, output_path=isolated_root / "out2.zip")
    with zipfile.ZipFile(result["zip_path"]) as z:
        names = z.namelist()
    assert "continuity/environment_bible/loc_brand_new_place.json" in names
    assert "continuity/prop_registry/prop_brand_new_thing.json" in names


def test_generated_requests_physically_in_zip(isolated_root):
    season_id, episode_id, job = _build_real_season(isolated_root)
    result = package_season(isolated_root, season_id, job, output_path=isolated_root / "out.zip")
    with zipfile.ZipFile(result["zip_path"]) as z:
        names = z.namelist()
    assert any(n.startswith("continuity/generated_requests/") for n in names)


def test_production_status_contains_season_acceptance(isolated_root):
    season_id, episode_id, job = _build_real_season(isolated_root)
    result = package_season(isolated_root, season_id, job, output_path=isolated_root / "out.zip")
    with zipfile.ZipFile(result["zip_path"]) as z:
        names = z.namelist()
        ps_name = [n for n in names if n.startswith("continuity/production_status/")][0]
        ps = json.loads(z.read(ps_name))
    assert ps["season_acceptance"] is not None
    assert "status" in ps["season_acceptance"]
    assert "note" in ps["season_acceptance"]


def test_manifest_count_and_file_list_exactly_match_reopened_zip(isolated_root):
    season_id, episode_id, job = _build_real_season(isolated_root)
    result = package_season(isolated_root, season_id, job, output_path=isolated_root / "out.zip")
    verify = verify_frozen_package(result["zip_path"])
    assert verify["count_matches"] is True
    assert verify["file_list_matches"] is True
    assert verify["files_in_zip_not_in_manifest"] == []
    assert verify["files_in_manifest_not_in_zip"] == []


def test_sha256_independently_reproducible(isolated_root):
    season_id, episode_id, job = _build_real_season(isolated_root)
    result = package_season(isolated_root, season_id, job, output_path=isolated_root / "out.zip")
    import hashlib
    independent_hash = hashlib.sha256(Path(result["zip_path"]).read_bytes()).hexdigest()
    assert independent_hash == result["sha256"]
    verify = verify_frozen_package(result["zip_path"])
    assert verify["sha256"] == result["sha256"]


def test_stale_manifest_detected_after_post_hoc_modification(isolated_root):
    season_id, episode_id, job = _build_real_season(isolated_root)
    result = package_season(isolated_root, season_id, job, output_path=isolated_root / "out.zip")

    verify_before = verify_frozen_package(result["zip_path"])
    assert verify_before["file_list_matches"] is True

    with zipfile.ZipFile(result["zip_path"], "a") as z:
        z.writestr("continuity/sneaked_in_file.json", "{}")

    verify_after = verify_frozen_package(result["zip_path"])
    assert verify_after["file_list_matches"] is False
    assert "continuity/sneaked_in_file.json" in verify_after["files_in_zip_not_in_manifest"]
    assert verify_after["count_matches"] is False


def test_registry_inclusion_is_reference_driven_not_whole_directory(isolated_root):
    (isolated_root / "continuity" / "character_bible").mkdir(parents=True, exist_ok=True)
    (isolated_root / "continuity" / "character_bible" / "char_999_unrelated.json").write_text(
        json.dumps({"character_id": "char_999_unrelated", "canonical_name": "Unrelated"}))
    season_id, episode_id, job = _build_real_season(isolated_root)
    result = package_season(isolated_root, season_id, job, output_path=isolated_root / "out.zip")
    with zipfile.ZipFile(result["zip_path"]) as z:
        names = z.namelist()
    assert "continuity/character_bible/char_999_unrelated.json" not in names
    assert "continuity/character_bible/char_001_zayd.json" in names


def test_collect_referenced_registry_ids_reads_real_episode_content(isolated_root):
    season_id, episode_id, job = _build_real_season(isolated_root, prop_ids=["prop_grocery_bag_01"])
    referenced = collect_referenced_registry_ids(isolated_root, [episode_id])
    assert "char_001_zayd" in referenced["character"]
    assert "loc_family_living_room" in referenced["environment"]
    assert "prop_grocery_bag_01" in referenced["prop"]
