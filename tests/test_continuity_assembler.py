import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.continuity.assembler import ContinuityAssembler
from tools.continuity.request_payload_builder import SceneClipSpec
from tools.providers.veo31 import Veo31Provider


def _spec(**overrides):
    base = dict(
        episode_id="ep_test_001",
        scene_id="scene_01",
        clip_id="clip_01",
        sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        secondary_character_ids=["char_002_amira"],
        environment_id="loc_family_living_room",
        prop_ids=["prop_grocery_bag_01"],
        camera={"shot": "medium", "axis": "stable-A"},
        lighting={"time_of_day": "afternoon"},
        emotions={"char_001_zayd": "curious"},
        music={"cue_id": None},
        raw_prompt_text="Zayd enters the living room holding a small grocery bag.",
        negative_constraints=["no duplicate characters"],
        previous_clip_id=None,
    )
    base.update(overrides)
    return SceneClipSpec(**base)


def test_process_first_clip_no_previous(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31Provider())
    request, payload, errors = assembler.process_clip(_spec())

    assert not any(e.severity == "error" for e in errors)
    assert request.clip_context["clip_id"] == "clip_01"
    assert len(request.reference_images) <= 3  # provider limit, not hardcoded in the test's assertion logic path
    assert request.generation_settings["duration_seconds"] == 8  # forced by reference image usage
    assert payload["model"] == "veo-3.1-generate-preview"
    assert "referenceImages" in payload["instances"][0]

    saved = assembler.clip_state_repo.load("ep_test_001", "scene_01", "clip_01")
    assert saved is not None
    assert saved.qa_status == "PENDING"
    assert saved.characters_present == ["char_001_zayd", "char_002_amira"]


def test_second_clip_reads_previous_clip_state(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31Provider())
    assembler.process_clip(_spec(clip_id="clip_01", sequence_index=1, previous_clip_id=None))

    request2, payload2, errors2 = assembler.process_clip(
        _spec(clip_id="clip_02", sequence_index=2, previous_clip_id="clip_01",
              raw_prompt_text="Zayd sets the grocery bag on the table.")
    )
    assert not any(e.severity == "error" for e in errors2)
    saved2 = assembler.clip_state_repo.load("ep_test_001", "scene_01", "clip_02")
    assert saved2.previous_clip_id == "clip_01"

    prev = assembler.clip_state_repo.get_previous_in_thread(saved2)
    assert prev is not None
    assert prev.clip_id == "clip_01"


def test_dropped_reference_notes_when_too_many_candidates(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31Provider())
    spec = _spec(
        primary_character_ids=["char_001_zayd"],
        # 4 characters with real reference images = 4 candidates, provider limit is 3.
        # (loc_family_living_room / prop_grocery_bag_01 currently have NO reference
        # images per the real migration report, so they can't be used to force this
        # in a live-data test -- confirms the "environments/props need images" risk
        # flagged in Phase 2's architecture doc is real, not hypothetical.)
        secondary_character_ids=["char_002_amira", "char_003_ummi_layla", "char_004_baba_ahmad"],
        environment_id=None,
        prop_ids=[],
    )
    request, _, _ = assembler.process_clip(spec)
    assert len(request.reference_images) == 3
    assert len(request.dropped_reference_notes) == 1
