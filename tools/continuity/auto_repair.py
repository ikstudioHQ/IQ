"""
tools/continuity/auto_repair.py

Consumes a QAReport (tools/continuity/qa_engine.py) and, only for
findings marked auto_repairable, rebuilds the SAME clip's request with
adjustments -- never touches any other clip, per the original brief's
"regenerate only affected clips when safe." Capped at
qa_engine.MAX_REPAIR_ATTEMPTS per clip so a genuinely unrepairable
issue (e.g. a permanently missing asset that keeps getting flagged)
can't loop forever; once the cap is hit, the clip is left in
NEEDS_HUMAN_REVIEW / BLOCKED_ON_DEPENDENCY for an actual person.

Two repair actions are implemented, both safe in the sense the brief
meant -- prompt/payload-level adjustments, not architecture changes:

- "force_reference_priority": a character/prop's reference image was
  dropped for budget reasons on the last attempt. Re-run the request
  with that owner forced to the front of the reference-image priority
  order (tools/continuity/reference_image_manager.py's Phase 5 addition).
- "rebuild_request": the request was built against continuity state
  that's since gone stale (e.g. environment bibles changed). Just
  rebuild fresh against current data -- no special parameters needed.

Findings NOT auto-repairable (missing asset, missing continuation
anchor, unresolved safety review) are deliberately left alone here --
they require a human or an external dependency, and pretending
otherwise would be worse than leaving them flagged.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from tools.continuity.assembler import ContinuityAssembler
from tools.continuity.clip_state import ClipStateRepo
from tools.continuity.qa_engine import MAX_REPAIR_ATTEMPTS, QAReport, get_report, run_structural_qa
from tools.continuity.request_payload_builder import SceneClipSpec

_OWNER_ID_FROM_NOTE = re.compile(r"^([\w.]+)\s*\(")


@dataclass
class AutoRepairResult:
    applied: bool
    reason: str
    new_report: Optional[QAReport] = None
    repair_attempt: int = 0


def _extract_forced_owner_ids(report: QAReport) -> list[str]:
    owners: list[str] = []
    for f in report.findings:
        if f.get("repair_action") != "force_reference_priority":
            continue
        if f.get("repair_target"):
            owners.append(f["repair_target"])
            continue
        m = _OWNER_ID_FROM_NOTE.match(f.get("message", ""))
        if m:
            owners.append(m.group(1))
    return owners


def _extract_extra_negative_constraints(report: QAReport) -> list[str]:
    constraints = []
    for f in report.findings:
        if f.get("tier") != "visual" or f.get("repair_action") != "force_reference_priority":
            continue
        target = f.get("repair_target", "the flagged character")
        constraints.append(
            f"ensure exactly one instance of {target}, exactly matching its locked "
            f"reference image -- no redesign, no duplication, no colour/wardrobe change"
        )
    return constraints


def apply_auto_repair(
    root: str | Path,
    assembler: ContinuityAssembler,
    spec: SceneClipSpec,
) -> AutoRepairResult:
    root = Path(root)
    clip_repo = ClipStateRepo(root)
    clip = clip_repo.load(spec.episode_id, spec.scene_id, spec.clip_id)
    if clip is None:
        return AutoRepairResult(applied=False, reason="clip_state not found -- run process_clip() first")

    if clip.repair_attempt >= MAX_REPAIR_ATTEMPTS:
        return AutoRepairResult(
            applied=False,
            reason=f"repair_attempt cap reached ({MAX_REPAIR_ATTEMPTS}) -- needs human review, not another automatic attempt",
            repair_attempt=clip.repair_attempt,
        )

    report = get_report(root, spec.episode_id, spec.scene_id, spec.clip_id) or \
        run_structural_qa(root, spec.episode_id, spec.scene_id, spec.clip_id)

    if report.overall_status != "NEEDS_REPAIR":
        return AutoRepairResult(
            applied=False,
            reason=f"overall_status={report.overall_status}, not eligible for automatic repair "
                   f"(either already PASS, or blocked on something this system can't fix itself)",
            new_report=report,
            repair_attempt=clip.repair_attempt,
        )

    forced_owner_ids = _extract_forced_owner_ids(report)
    extra_negative_constraints = _extract_extra_negative_constraints(report)

    assembler.process_clip(
        spec,
        forced_reference_owner_ids=forced_owner_ids or None,
        extra_negative_constraints=extra_negative_constraints or None,
    )

    # process_clip() writes a fresh ClipState (repair_attempt defaults to 0)
    # -- preserve and increment the counter across the rebuild explicitly,
    # rather than changing process_clip()'s own contract.
    rebuilt = clip_repo.load(spec.episode_id, spec.scene_id, spec.clip_id)
    rebuilt.repair_attempt = clip.repair_attempt + 1
    clip_repo.save(rebuilt)

    new_report = run_structural_qa(root, spec.episode_id, spec.scene_id, spec.clip_id)

    return AutoRepairResult(
        applied=True,
        reason=f"rebuilt with forced_reference_owner_ids={forced_owner_ids}, "
               f"{len(extra_negative_constraints)} extra negative constraint(s) added",
        new_report=new_report,
        repair_attempt=rebuilt.repair_attempt,
    )
