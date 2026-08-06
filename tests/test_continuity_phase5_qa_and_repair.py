import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.continuity.assembler import ContinuityAssembler
from tools.continuity.auto_repair import apply_auto_repair
from tools.continuity.qa_engine import (
    MAX_REPAIR_ATTEMPTS,
    get_report,
    register_visual_qa_result,
    run_structural_qa,
)
from tools.continuity.request_payload_builder import SceneClipSpec
from tools.continuity.request_serializer import load_serialized_request
from tools.providers.veo31_fast import Veo31FastProvider


def _process(assembler, **overrides):
    base = dict(
        episode_id="ep_qa", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        environment_id="loc_family_living_room",
        raw_prompt_text="Zayd walks through the room.",
    )
    base.update(overrides)
    spec = SceneClipSpec(**base)
    assembler.process_clip(spec)
    return spec


def test_clean_clip_passes_structural_qa(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    _process(assembler)
    report = run_structural_qa(isolated_root, "ep_qa", "s1", "c1")
    assert report.overall_status == "PASS"
    assert report.findings == []


def test_run_structural_qa_requires_existing_clip(isolated_root):
    try:
        run_structural_qa(isolated_root, "no_such", "s1", "c1")
        assert False, "should have raised"
    except ValueError:
        pass


def test_budget_drop_flagged_and_marked_auto_repairable(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    spec = SceneClipSpec(
        episode_id="ep_qa_budget", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        secondary_character_ids=["char_002_amira", "char_003_ummi_layla", "char_004_baba_ahmad"],
        raw_prompt_text="A family scene.",
    )
    assembler.process_clip(spec)
    report = run_structural_qa(isolated_root, "ep_qa_budget", "s1", "c1")
    gap_findings = [f for f in report.findings if f["check_id"] == "reference_lock_gap"]
    assert len(gap_findings) == 1
    assert gap_findings[0]["auto_repairable"] is True
    assert report.overall_status == "NEEDS_REPAIR"


def test_auto_repair_forces_dropped_character_into_next_attempt(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    spec = SceneClipSpec(
        episode_id="ep_qa_budget2", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        secondary_character_ids=["char_002_amira", "char_003_ummi_layla", "char_004_baba_ahmad"],
        raw_prompt_text="A family scene.",
    )
    assembler.process_clip(spec)
    bundle_before = load_serialized_request(isolated_root, "ep_qa_budget2", "s1", "c1")
    dropped_owner = bundle_before["request"]["dropped_reference_notes"][0].split(" (")[0]

    result = apply_auto_repair(isolated_root, assembler, spec)
    assert result.applied is True
    assert result.repair_attempt == 1

    bundle_after = load_serialized_request(isolated_root, "ep_qa_budget2", "s1", "c1")
    used_owners = [r["owner_id"] for r in bundle_after["request"]["reference_images"]]
    assert dropped_owner in used_owners  # the previously-dropped character is now included


def test_repair_attempt_cap_stops_the_loop(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    spec = SceneClipSpec(
        episode_id="ep_qa_cap", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        secondary_character_ids=["char_002_amira", "char_003_ummi_layla", "char_004_baba_ahmad"],
        raw_prompt_text="A family scene.",
    )
    assembler.process_clip(spec)
    for _ in range(MAX_REPAIR_ATTEMPTS):
        r = apply_auto_repair(isolated_root, assembler, spec)
        assert r.applied is True
    over_cap = apply_auto_repair(isolated_root, assembler, spec)
    assert over_cap.applied is False
    assert "cap reached" in over_cap.reason


def test_missing_continuation_anchor_not_auto_repairable(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    _process(assembler, episode_id="ep_qa_anchor", clip_id="c2", sequence_index=2, previous_clip_id="c1")
    report = run_structural_qa(isolated_root, "ep_qa_anchor", "s1", "c2")
    anchor_findings = [f for f in report.findings if f["check_id"] == "continuity_anchor_gap"]
    assert len(anchor_findings) == 1
    assert anchor_findings[0]["auto_repairable"] is False
    # a non-repairable warning alone must not force NEEDS_REPAIR
    assert report.overall_status == "PASS"


def test_unresolved_safety_review_surfaces_as_structural_finding(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    _process(assembler, episode_id="ep_qa_safety",
             raw_prompt_text="The children are playing with fire near the tent.")
    report = run_structural_qa(isolated_root, "ep_qa_safety", "s1", "c1")
    assert any(f["check_id"] == "unresolved_safety_review" for f in report.findings)


def test_visual_qa_rejects_unknown_category(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    _process(assembler, episode_id="ep_qa_badcat")
    try:
        register_visual_qa_result(isolated_root, "ep_qa_badcat", "s1", "c1", [
            {"category": "not_a_real_category", "message": "x"}
        ], reviewed_by="tester")
        assert False, "should have raised"
    except ValueError:
        pass


def test_visual_qa_character_drift_flows_into_repair(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    _process(assembler, episode_id="ep_qa_drift")
    report = register_visual_qa_result(isolated_root, "ep_qa_drift", "s1", "c1", [
        {"category": "character_drift", "severity": "error",
         "message": "Colour drifted from locked reference.",
         "auto_repairable": True, "repair_action": "force_reference_priority",
         "repair_target": "char_001_zayd"},
    ], reviewed_by="human_reviewer")
    assert report.overall_status == "NEEDS_REPAIR"
    assert report.reviewed_by == "human_reviewer"

    spec = SceneClipSpec(
        episode_id="ep_qa_drift", scene_id="s1", clip_id="c1", sequence_index=1,
        primary_character_ids=["char_001_zayd"],
        raw_prompt_text="Zayd walks through the room.",
    )
    result = apply_auto_repair(isolated_root, assembler, spec)
    assert result.applied is True

    bundle = load_serialized_request(isolated_root, "ep_qa_drift", "s1", "c1")
    assert any("char_001_zayd" in c for c in bundle["request"]["negative_constraints"])


def test_visual_qa_non_repairable_finding_forces_human_review(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    _process(assembler, episode_id="ep_qa_human")
    report = register_visual_qa_result(isolated_root, "ep_qa_human", "s1", "c1", [
        {"category": "duplicate_characters", "severity": "error",
         "message": "Two instances of Zayd appeared in frame -- not fixable by reprioritizing references alone.",
         "auto_repairable": False},
    ], reviewed_by="human_reviewer")
    assert report.overall_status == "NEEDS_HUMAN_REVIEW"


def test_structural_qa_rerun_does_not_duplicate_visual_findings(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    _process(assembler, episode_id="ep_qa_persist")
    register_visual_qa_result(isolated_root, "ep_qa_persist", "s1", "c1", [
        {"category": "lighting_drift", "severity": "warning", "message": "Slightly warmer than locked.",
         "auto_repairable": False},
    ], reviewed_by="human_reviewer")
    report1 = run_structural_qa(isolated_root, "ep_qa_persist", "s1", "c1")
    report2 = run_structural_qa(isolated_root, "ep_qa_persist", "s1", "c1")
    visual1 = [f for f in report1.findings if f["tier"] == "visual"]
    visual2 = [f for f in report2.findings if f["tier"] == "visual"]
    assert len(visual1) == 1
    assert len(visual2) == 1  # re-running structural QA must not duplicate the preserved visual finding


def test_get_report_returns_none_when_no_qa_run_yet(isolated_root):
    assembler = ContinuityAssembler(str(isolated_root), Veo31FastProvider())
    _process(assembler, episode_id="ep_qa_none")
    assert get_report(isolated_root, "ep_qa_none", "s1", "c1") is None
