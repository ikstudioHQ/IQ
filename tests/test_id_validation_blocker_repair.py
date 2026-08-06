import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.authoring.manual_author_seam import register_authored_episode, register_season_concept
from tools.authoring.scene_to_clip_bridge import build_clip_specs
from tools.authoring.schemas import EpisodeScript
from tools.continuity.assembler import ContinuityAssembler
from tools.continuity.id_validation import validate_registry_ids
from tools.continuity.request_payload_builder import SceneClipSpec
from tools.orchestration.season_orchestrator import generate_season
from tools.providers.veo31_fast import Veo31FastProvider


# 1. Nonexistent character
def test_nonexistent_character_blocked(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    spec = SceneClipSpec(
        episode_id="blk1", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_999_fake"],
        raw_prompt_text="A fake character appears.",
    )
    req, payload, errors = assembler.process_clip(spec)
    assert req.has_blocking_issues()
    assert payload == {}
    assert any(d["id_type"] == "character" and d["invalid_id"] == "char_999_fake" for d in req.diagnostics)


# 2. Nonexistent environment
def test_nonexistent_environment_blocked(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    spec = SceneClipSpec(
        episode_id="blk2", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        environment_id="loc_999_fake",
        raw_prompt_text="A fake place.",
    )
    req, payload, errors = assembler.process_clip(spec)
    assert req.has_blocking_issues()
    assert payload == {}
    assert any(d["id_type"] == "environment" and d["invalid_id"] == "loc_999_fake" for d in req.diagnostics)


# 3. Nonexistent prop
def test_nonexistent_prop_blocked(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    spec = SceneClipSpec(
        episode_id="blk3", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        prop_ids=["prop_999_fake"],
        raw_prompt_text="A fake prop.",
    )
    req, payload, errors = assembler.process_clip(spec)
    assert req.has_blocking_issues()
    assert payload == {}
    assert any(d["id_type"] == "prop" and d["invalid_id"] == "prop_999_fake" for d in req.diagnostics)


# 4. Mixed valid + invalid IDs
def test_mixed_valid_and_invalid_ids_reports_only_the_invalid_one(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    spec = SceneClipSpec(
        episode_id="blk4", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],       # valid
        secondary_character_ids=["char_999_fake"],      # invalid
        environment_id="loc_family_living_room",         # valid
        prop_ids=["prop_grocery_bag_01"],                # valid
        raw_prompt_text="Mixed valid and invalid references.",
    )
    req, payload, errors = assembler.process_clip(spec)
    assert req.has_blocking_issues()
    assert payload == {}
    # exactly the invalid one is named, nothing else
    invalid_ids = [d["invalid_id"] for d in req.diagnostics]
    assert invalid_ids == ["char_999_fake"]


# 5. Raw internal-ID leakage prevention
def test_raw_id_never_appears_in_prompt_or_payload(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    spec = SceneClipSpec(
        episode_id="blk5", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_999_totally_fake"],
        raw_prompt_text='char_999_totally_fake says: "Hello there!"',  # simulates the bridge's own composed leak
    )
    req, payload, errors = assembler.process_clip(spec)
    assert "char_999_totally_fake" not in req.prompt
    assert payload == {}

    from tools.continuity.request_serializer import load_serialized_request
    bundle = load_serialized_request(isolated_root, "blk5", "s1", "c1")
    assert "char_999_totally_fake" not in bundle["request"]["prompt"]
    assert bundle["provider_payload"] is None
    assert bundle["status"] == "BLOCKED"

    # Defense-in-depth: the bridge's own composed text (even before this
    # gate) no longer treats an unknown ID as a plausible name either.
    from tools.authoring.scene_to_clip_bridge import _compose_prompt_text
    text = _compose_prompt_text(isolated_root, [
        {"kind": "dialogue", "character_id": "char_999_totally_fake", "text": "Hello.", "emotion": None}
    ], {})
    assert "[unknown character: char_999_totally_fake]" in text


# 6. Valid existing content regression -- real Phase 6 fixture content must be unaffected
def test_valid_existing_content_still_works(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    spec = SceneClipSpec(
        episode_id="blk6", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        secondary_character_ids=["char_002_amira"],
        environment_id="loc_family_living_room",
        prop_ids=["prop_grocery_bag_01"],
        raw_prompt_text="Zayd and Amira talk in the living room.",
    )
    req, payload, errors = assembler.process_clip(spec)
    assert not req.has_blocking_issues()
    assert payload != {}
    assert req.diagnostics == []
    assert "Zayd and Amira talk" in req.prompt


def test_validate_registry_ids_directly_all_valid_returns_empty(repo_root):
    errors = validate_registry_ids(
        repo_root, character_ids=["char_001_zayd", "char_002_amira"],
        environment_id="loc_family_living_room", prop_ids=["prop_grocery_bag_01"],
    )
    assert errors == []


def test_validate_registry_ids_none_environment_is_not_an_error(repo_root):
    errors = validate_registry_ids(repo_root, character_ids=["char_001_zayd"], environment_id=None, prop_ids=[])
    assert errors == []


# 7. Orchestrator fail-closed behavior
def test_orchestrator_fails_closed_on_invalid_character(isolated_root):
    register_season_concept(isolated_root, {
        "season_id": "blk7", "theme": "t", "language": "English", "target_age": "5-8",
        "episode_count": 1, "episode_duration_minutes": 5,
        "premises": [{"episode_id": "blk7_ep", "title": "t", "premise": "t", "arc_position": "opener"}],
    })
    register_authored_episode(isolated_root, "blk7", {
        "episode_id": "blk7_ep", "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
        "scenes": [{
            "scene_id": "s1", "location_id": "loc_family_living_room",
            "characters_present": ["char_999_fake"], "props_visible": [], "environment_overrides": {},
            "beats": [{"beat_id": "b1", "kind": "dialogue", "character_id": "char_999_fake",
                       "text": "A character who should never exist.", "estimated_seconds": None}],
        }],
        "song": None, "story_updates": {},
    })
    # This test proves ID-validation blocking specifically (Phase 8's
    # confirmed blocker), not production-gate behavior -- explicitly
    # disable gates so the trivial single-beat fixture reaches the
    # request-build stage this test actually targets.
    from tools.orchestration.testing_overrides import DisableProductionGatesForTesting
    state = generate_season(isolated_root, season_id="blk7", theme="t", episode_count=1,
                             episode_duration_minutes=5, language="English", target_age="5-8",
                             author_provider=None, veo_executor=None,
                             _test_only_disable_gates=DisableProductionGatesForTesting(
                                 reason="testing ID-validation blocking, not production gates"))
    ep = state["episodes"]["blk7_ep"]
    clip = list(ep["clips"].values())[0]
    assert clip["status"] == "BLOCKED"
    assert "char_999_fake" in clip["last_error"]
    assert ep["status"] == "INCOMPLETE"

    from tools.continuity.request_serializer import load_serialized_request
    bundle = load_serialized_request(isolated_root, "blk7_ep", "s1", "clip_01")
    assert bundle["status"] == "BLOCKED"
    assert bundle["provider_payload"] is None
    assert "char_999_fake" not in bundle["request"]["prompt"]
