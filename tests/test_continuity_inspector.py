import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.continuity.assembler import ContinuityAssembler
from tools.continuity.inspector import inspect
from tools.continuity.request_payload_builder import SceneClipSpec
from tools.providers.veo31_fast import Veo31FastProvider


def test_inspect_missing_clip_gives_helpful_message(isolated_root):
    report = inspect(isolated_root, "no_such_ep", "scene_01", "clip_01")
    assert "No clip_state found" in report


def test_inspect_reports_attached_and_missing_images(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    spec = SceneClipSpec(
        episode_id="ep_inspect", scene_id="scene_01", clip_id="clip_01", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        secondary_character_ids=[],
        environment_id="loc_family_living_room",
        prop_ids=["prop_grocery_bag_01"],
        raw_prompt_text="Zayd walks into the room.",
        previous_clip_id=None,
    )
    assembler.process_clip(spec)
    report = inspect(isolated_root, "ep_inspect", "scene_01", "clip_01")

    assert "char_001_zayd (reference image attached)" in report
    assert "loc_family_living_room (no reference image available" in report
    assert "prop_grocery_bag_01 (no reference image available" in report
    assert "first clip in thread" in report
    assert "PENDING" in report
    assert "veo-3.1-fast" in report
