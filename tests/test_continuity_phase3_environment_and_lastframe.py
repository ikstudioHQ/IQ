import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.continuity.assembler import ContinuityAssembler
from tools.continuity.clip_output_registrar import register_clip_output, video_extension_still_valid
from tools.continuity.environment_bible import EnvironmentBibleRepo
from tools.continuity.request_payload_builder import SceneClipSpec
from tools.providers.veo31_fast import Veo31FastProvider


def _rebuild_index(root):
    subprocess.run(
        [sys.executable, str(ROOT / "tools/continuity/rebuild_clip_state_index.py"), str(root)],
        check=True, capture_output=True,
    )


def test_environment_bible_repo_loads_real_location(repo_root):
    repo = EnvironmentBibleRepo(repo_root)
    bible = repo.get("loc_family_living_room")
    assert bible is not None
    assert bible["display_name"]
    notes = repo.continuity_notes("loc_family_living_room")
    assert notes is not None


def test_environment_bible_unknown_location_returns_none(repo_root):
    repo = EnvironmentBibleRepo(repo_root)
    assert repo.get("loc_does_not_exist") is None


def test_first_clip_no_previous_no_continuation(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    spec = SceneClipSpec(
        episode_id="ep_env1", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        environment_id="loc_family_living_room",
        raw_prompt_text="Zayd walks in.",
    )
    req, _, _ = assembler.process_clip(spec)
    assert req.continuation_mode is None
    assert req.previous_frame_image is None


def test_environment_carries_forward_when_not_overridden(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    spec1 = SceneClipSpec(
        episode_id="ep_env2", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        environment_id="loc_family_living_room",
        lighting={"time_of_day": "evening", "tone": "dim lamp light"},
        raw_prompt_text="Zayd walks in at evening.",
    )
    assembler.process_clip(spec1)
    _rebuild_index(isolated_root)

    spec2 = SceneClipSpec(
        episode_id="ep_env2", scene_id="s1", clip_id="c2", sequence_index=2,
        primary_character_ids=["char_001_zayd"],
        environment_id="loc_family_living_room",
        lighting={},  # nothing specified -- must carry forward
        raw_prompt_text="Zayd sits down.",
        previous_clip_id="c1",
    )
    req2, _, _ = assembler.process_clip(spec2)
    assert req2.environment_metadata["time_of_day"] == "evening"
    assert req2.environment_provenance["time_of_day"] == "carried_forward"


def test_explicit_environment_override_wins_over_carry_forward(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    spec1 = SceneClipSpec(
        episode_id="ep_env3", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        environment_id="loc_family_living_room",
        lighting={"time_of_day": "evening"},
        raw_prompt_text="Evening.",
    )
    assembler.process_clip(spec1)
    _rebuild_index(isolated_root)

    spec2 = SceneClipSpec(
        episode_id="ep_env3", scene_id="s1", clip_id="c2", sequence_index=2,
        primary_character_ids=["char_001_zayd"],
        environment_id="loc_family_living_room",
        lighting={"time_of_day": "morning"},  # story explicitly jumps to next morning
        raw_prompt_text="The next morning.",
        previous_clip_id="c1",
    )
    req2, _, _ = assembler.process_clip(spec2)
    assert req2.environment_metadata["time_of_day"] == "morning"
    assert req2.environment_provenance["time_of_day"] == "explicit"


def test_continuity_note_folded_into_negative_constraints(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    spec = SceneClipSpec(
        episode_id="ep_env4", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        environment_id="loc_family_living_room",
        raw_prompt_text="Zayd looks around the room.",
    )
    req, _, _ = assembler.process_clip(spec)
    assert any("environment continuity" in c for c in req.negative_constraints)


def test_video_extension_still_valid_within_window():
    output = {
        "video_reference": "veo://x.mp4",
        "video_retention_expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
    }
    assert video_extension_still_valid(output) is True


def test_video_extension_invalid_after_expiry():
    output = {
        "video_reference": "veo://x.mp4",
        "video_retention_expires_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
    }
    assert video_extension_still_valid(output) is False


def test_video_extension_invalid_with_no_video_reference():
    assert video_extension_still_valid({}) is False


def test_register_clip_output_requires_existing_clip_state(isolated_root):
    provider = Veo31FastProvider()
    try:
        register_clip_output(
            isolated_root, "no_such_ep", "s1", "c1",
            provider_capabilities=provider.capabilities(),
        )
        assert False, "should have raised"
    except ValueError:
        pass


def test_video_extension_chosen_over_first_frame_when_both_valid(isolated_root):
    provider = Veo31FastProvider()
    assembler = ContinuityAssembler(str(isolated_root), provider)
    spec1 = SceneClipSpec(
        episode_id="ep_env5", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        environment_id="loc_family_living_room",
        raw_prompt_text="Zayd enters.",
    )
    assembler.process_clip(spec1)
    register_clip_output(
        isolated_root, "ep_env5", "s1", "c1",
        provider_capabilities=provider.capabilities(),
        video_reference="veo://fresh.mp4",
        last_frame_path="continuity/frames/ep_env5/s1/c1_last_frame.jpg",
    )
    _rebuild_index(isolated_root)

    spec2 = SceneClipSpec(
        episode_id="ep_env5", scene_id="s1", clip_id="c2", sequence_index=2,
        primary_character_ids=["char_001_zayd"],
        environment_id="loc_family_living_room",
        raw_prompt_text="Zayd continues.",
        previous_clip_id="c1",
    )
    req2, _, _ = assembler.process_clip(spec2)
    assert req2.continuation_mode == "video_extension"
    assert req2.previous_frame_image == "veo://fresh.mp4"


def test_expired_video_falls_back_to_first_frame(isolated_root):
    provider = Veo31FastProvider()
    assembler = ContinuityAssembler(str(isolated_root), provider)
    spec1 = SceneClipSpec(
        episode_id="ep_env6", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        environment_id="loc_family_living_room",
        raw_prompt_text="Zayd enters.",
    )
    assembler.process_clip(spec1)
    register_clip_output(
        isolated_root, "ep_env6", "s1", "c1",
        provider_capabilities=provider.capabilities(),
        video_reference="veo://old.mp4",
        last_frame_path="continuity/frames/ep_env6/s1/c1_last_frame.jpg",
        generated_at=datetime.now(timezone.utc) - timedelta(days=3),
    )
    _rebuild_index(isolated_root)

    spec2 = SceneClipSpec(
        episode_id="ep_env6", scene_id="s1", clip_id="c2", sequence_index=2,
        primary_character_ids=["char_001_zayd"],
        environment_id="loc_family_living_room",
        raw_prompt_text="Zayd continues.",
        previous_clip_id="c1",
    )
    req2, _, _ = assembler.process_clip(spec2)
    assert req2.continuation_mode == "first_frame"
    assert req2.previous_frame_image == "continuity/frames/ep_env6/s1/c1_last_frame.jpg"
