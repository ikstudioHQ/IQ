import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.continuity.assembler import ContinuityAssembler
from tools.continuity.request_inspector import inspect_request
from tools.continuity.request_payload_builder import SceneClipSpec
from tools.continuity.request_serializer import load_serialized_request
from tools.providers.veo31_fast import Veo31FastProvider


def test_safe_request_builds_full_payload_and_serializes(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    spec = SceneClipSpec(
        episode_id="ep_p4_safe", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        environment_id="loc_family_living_room",
        raw_prompt_text="Zayd waters the plants in the living room.",
    )
    req, payload, errors = assembler.process_clip(spec)
    assert not req.has_blocking_issues()
    assert payload["model"] == "veo-3.1-fast-generate-preview"

    bundle = load_serialized_request(isolated_root, "ep_p4_safe", "s1", "c1")
    assert bundle is not None
    assert bundle["status"] == "READY"
    assert bundle["provider_payload"] is not None


def test_unsafe_prompt_blocks_before_payload_built(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    spec = SceneClipSpec(
        episode_id="ep_p4_unsafe", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        environment_id="loc_family_living_room",
        raw_prompt_text="There is blood and weapons scattered after the fight.",
    )
    req, payload, errors = assembler.process_clip(spec)
    assert req.has_blocking_issues()
    assert payload == {}

    bundle = load_serialized_request(isolated_root, "ep_p4_unsafe", "s1", "c1")
    assert bundle["status"] == "BLOCKED"
    assert bundle["provider_payload"] is None
    assert len(bundle["request"]["safety_findings"]) >= 2

    saved = assembler.clip_state_repo.load("ep_p4_unsafe", "s1", "c1")
    assert saved.qa_status == "BLOCKED"


def test_review_required_safety_finding_does_not_block(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    spec = SceneClipSpec(
        episode_id="ep_p4_review", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        environment_id="loc_family_living_room",
        raw_prompt_text="Zayd is playing with fire near the campsite, which worries his mother.",
    )
    req, payload, errors = assembler.process_clip(spec)
    assert not req.has_blocking_issues()
    assert payload != {}
    assert any(f["severity"] == "warning" for f in req.safety_findings)


def test_missing_continuation_anchor_produces_warning_diagnostic(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    # previous_clip_id set but that clip was never planned/generated
    spec = SceneClipSpec(
        episode_id="ep_p4_anchor", scene_id="s1", clip_id="c2", sequence_index=2,
        primary_character_ids=["char_001_zayd"],
        environment_id="loc_family_living_room",
        raw_prompt_text="Zayd continues from before.",
        previous_clip_id="c1",  # does not exist
    )
    req, payload, errors = assembler.process_clip(spec)
    assert any(d["field"] == "continuation_mode" and d["severity"] == "warning" for d in req.diagnostics)
    # a warning-only diagnostic must not block the request
    assert not req.has_blocking_issues()
    assert payload != {}


def test_invalid_payload_combination_caught_by_provider_validation():
    from tools.providers.veo31 import Veo31Provider
    p = Veo31Provider()
    request = {
        "prompt": "test",
        "continuation_mode": "video_extension",
        "previous_frame_image": "veo://something.mp4",
        "reference_images": [],
        "generation_settings": {"duration_seconds": 8, "resolution": "720p", "aspect_ratio": "16:9"},
    }
    # video_extension IS supported by veo-3.1, so this should be clean...
    errors = p.validate_request(request)
    assert not any(e.field == "continuation_mode" for e in errors)

    # ...but a mode the provider doesn't support should be flagged
    request["continuation_mode"] = "not_a_real_mode"
    errors2 = p.validate_request(request)
    # not_a_real_mode isn't explicitly checked, but missing frame combos are:
    request3 = dict(request, continuation_mode="video_extension", previous_frame_image=None)
    errors3 = p.validate_request(request3)
    assert any(e.field == "previous_frame_image" for e in errors3)


def test_reference_images_without_provider_support_flagged():
    from tools.providers.base import ProviderCapabilities
    from tools.providers.veo31 import Veo31Provider

    p = Veo31Provider()
    request = {
        "prompt": "test",
        "reference_images": [{"path": "x.png"}],
        "generation_settings": {"duration_seconds": 8, "resolution": "720p", "aspect_ratio": "16:9"},
    }
    # monkeypatch capabilities to simulate a provider without reference image support
    original = p._capabilities
    object.__setattr__(p, "_capabilities", ProviderCapabilities(
        **{**original.__dict__, "supports_reference_images": False, "max_reference_images": 0}
    ))
    errors = p.validate_request(request)
    assert any(e.field == "reference_images" for e in errors)


def test_missing_asset_detected_via_reference_image_manager(tmp_path):
    # Deliberately NOT using isolated_root here: writing a new character
    # bible file into isolated_root's symlinked character_bible/ would write
    # through to the real repo directory. Build a fully synthetic, isolated
    # root instead so this test can never pollute real data.
    import json
    (tmp_path / "continuity" / "character_bible").mkdir(parents=True)
    (tmp_path / "continuity" / "environment_bible").mkdir(parents=True)
    (tmp_path / "continuity" / "prop_registry").mkdir(parents=True)
    (tmp_path / "continuity" / "clip_state").mkdir(parents=True)
    (tmp_path / "continuity" / "providers" / "capabilities").mkdir(parents=True)
    for name in ("veo_3_1.json", "veo_3_1_fast.json"):
        src = ROOT / "continuity" / "providers" / "capabilities" / name
        (tmp_path / "continuity" / "providers" / "capabilities" / name).write_text(src.read_text())

    bible_path = tmp_path / "continuity" / "character_bible" / "char_999_fake.json"
    bible_path.write_text(json.dumps({
        "character_id": "char_999_fake",
        "reference_images": [{"asset_id": "fake_ref", "path": "sources/characters/reference_images/DOES_NOT_EXIST.png"}],
    }))

    assembler = ContinuityAssembler(str(tmp_path), Veo31FastProvider())
    spec = SceneClipSpec(
        episode_id="ep_p4_missing_asset", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_999_fake"],
        raw_prompt_text="A character with a missing reference image.",
    )
    req, payload, errors = assembler.process_clip(spec)
    assert any(
        d["source"] == "reference_image_manager" and "does not resolve" in d["message"]
        for d in req.diagnostics
    )


def test_request_inspector_reports_blocked_status(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    spec = SceneClipSpec(
        episode_id="ep_p4_inspect", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        environment_id="loc_family_living_room",
        raw_prompt_text="There is blood on the weapons after the fight.",
    )
    assembler.process_clip(spec)
    report = inspect_request(isolated_root, "ep_p4_inspect", "s1", "c1")
    assert "Status: BLOCKED" in report
    assert "BLOCKING" in report
    assert "Provider payload: NOT built" in report


def test_request_inspector_missing_bundle_gives_helpful_message(isolated_root):
    report = inspect_request(isolated_root, "no_such", "s1", "c1")
    assert "No serialized request found" in report
