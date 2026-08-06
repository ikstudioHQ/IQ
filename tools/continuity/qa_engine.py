"""
tools/continuity/qa_engine.py

Two tiers of QA, deliberately not conflated:

TIER A -- structural. Fully automatic, runs on data this system already
has (clip_state, the serialized request, today's bibles). Catches:
reference images that were requested but silently dropped, missing
continuation anchors, environment state that's gone stale relative to
what the bibles/carry-forward would produce today, and unresolved
safety review-required warnings.

TIER B -- visual. character_drift, duplicate_characters, missing_props,
wardrobe_drift, lighting_drift, camera_drift -- exactly the taxonomy
from the original brief. These require looking at actual rendered
pixels against reference images, which this pipeline cannot do itself
(no vision-capable tool is wired up, and this sandbox's network
allowlist doesn't reach any image/video analysis API). Real findings
come in through register_visual_qa_result() -- from a human reviewing
the clip today, or a real vision-model call later. Either way, they
feed the exact same QAReport/auto-repair machinery as Tier A findings.
Nothing here ever fabricates a Tier B result.

Auto-Repair consumes findings from both tiers identically and decides,
per finding, whether it's safe to fix by rebuilding the request
(stronger negative constraints, forced reference-image priority) or
whether it's blocked on something outside this system's control (a
missing asset, an unrepaired previous clip). Capped at
MAX_REPAIR_ATTEMPTS per clip so a genuinely broken asset can't loop
forever.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from tools.continuity.clip_state import ClipStateRepo
from tools.continuity.environment_continuity import EnvironmentContinuityResolver
from tools.continuity.request_serializer import load_serialized_request

MAX_REPAIR_ATTEMPTS = 2

VISUAL_CATEGORIES = {
    "character_drift", "duplicate_characters", "missing_props",
    "wardrobe_drift", "lighting_drift", "camera_drift",
}


@dataclass
class QAFinding:
    check_id: str
    category: str
    tier: str  # "structural" | "visual"
    severity: str  # "error" | "warning"
    message: str
    auto_repairable: bool
    repair_action: Optional[str] = None  # "force_reference_priority" | "rebuild_request" | None
    repair_target: Optional[str] = None  # e.g. a character_id the repair action applies to


@dataclass
class QAReport:
    episode_id: str
    scene_id: str
    clip_id: str
    findings: list[dict] = field(default_factory=list)
    overall_status: str = "PASS"  # PASS | NEEDS_REPAIR | NEEDS_HUMAN_REVIEW | BLOCKED_ON_DEPENDENCY
    reviewed_by: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: str = "1.0"

    def to_dict(self) -> dict:
        return asdict(self)


def _report_path(root: str | Path, episode_id: str, scene_id: str, clip_id: str) -> Path:
    return Path(root) / "continuity" / "qa_reports" / episode_id / scene_id / f"{clip_id}.json"


def _load_report(root: str | Path, episode_id: str, scene_id: str, clip_id: str) -> QAReport:
    path = _report_path(root, episode_id, scene_id, clip_id)
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return QAReport(**{k: v for k, v in data.items() if k in QAReport.__dataclass_fields__})
    return QAReport(episode_id=episode_id, scene_id=scene_id, clip_id=clip_id)


def _save_report(root: str | Path, report: QAReport) -> Path:
    path = _report_path(root, report.episode_id, report.scene_id, report.clip_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _recompute_status(report: QAReport) -> None:
    errors = [f for f in report.findings if f["severity"] == "error"]
    if errors:
        if all(f["auto_repairable"] for f in errors):
            report.overall_status = "NEEDS_REPAIR"
        elif any(f["tier"] == "visual" for f in errors):
            report.overall_status = "NEEDS_HUMAN_REVIEW"
        else:
            report.overall_status = "BLOCKED_ON_DEPENDENCY"
        return
    # No blocking errors. A warning-level finding that's still marked
    # auto_repairable (e.g. a reference image dropped for budget reasons --
    # not wrong, just improvable) is still worth an automatic repair pass,
    # even though the request itself was never blocked from being sent.
    if any(f["auto_repairable"] for f in report.findings):
        report.overall_status = "NEEDS_REPAIR"
    else:
        report.overall_status = "PASS"


def run_structural_qa(root: str | Path, episode_id: str, scene_id: str, clip_id: str) -> QAReport:
    """Tier A. Safe to call any time after ContinuityAssembler.process_clip()
    -- reads only data already on disk, makes no assumptions about whether
    the clip has actually been generated yet."""
    root = Path(root)
    clip_repo = ClipStateRepo(root)
    clip = clip_repo.load(episode_id, scene_id, clip_id)
    if clip is None:
        raise ValueError(f"No clip_state found for {episode_id}/{scene_id}/{clip_id}")

    bundle = load_serialized_request(root, episode_id, scene_id, clip_id)
    findings: list[QAFinding] = []

    if bundle:
        for note in bundle["request"].get("dropped_reference_notes", []):
            findings.append(QAFinding(
                check_id="reference_lock_gap",
                category="reference_lock_gap",
                tier="structural",
                severity="warning",
                message=note,
                auto_repairable="exceeds provider limit" in note,
                repair_action="force_reference_priority" if "exceeds provider limit" in note else None,
            ))
        for d in bundle["request"].get("diagnostics", []):
            if d["field"] == "continuation_mode":
                findings.append(QAFinding(
                    check_id="continuity_anchor_gap",
                    category="continuity_anchor_gap",
                    tier="structural",
                    severity="warning",
                    message=d["message"],
                    auto_repairable=False,
                ))
            elif d["source"] == "reference_image_manager":
                findings.append(QAFinding(
                    check_id="missing_asset",
                    category="reference_lock_gap",
                    tier="structural",
                    severity="warning",
                    message=d["message"],
                    auto_repairable=False,
                ))
        for f in bundle["request"].get("safety_findings", []):
            if f["severity"] == "warning":
                findings.append(QAFinding(
                    check_id="unresolved_safety_review",
                    category="safety_review_required",
                    tier="structural",
                    severity="warning",
                    message=f["message"],
                    auto_repairable=False,
                ))

    if clip.environment.get("location_id") and bundle:
        resolver = EnvironmentContinuityResolver(root)
        fresh_env, _ = resolver.resolve(
            clip.environment["location_id"], {}, exclude_clip_id=clip_id,
        )
        original_provenance = bundle["request"].get("environment_provenance", {})
        # Only re-validate fields that were carried forward or defaulted --
        # an author's explicit override is a deliberate choice and must
        # never be "corrected" by re-resolving against blank overrides,
        # or every explicitly-overridden clip would false-positive here.
        checkable_fields = {
            k for k, prov in original_provenance.items() if prov != "explicit"
        }
        stale_fields = {
            k for k in checkable_fields
            if k in fresh_env and k in clip.lighting and fresh_env[k] != clip.lighting.get(k)
        }
        if stale_fields:
            findings.append(QAFinding(
                check_id="environment_state_stale",
                category="environment_drift",
                tier="structural",
                severity="error",
                message=(
                    f"Environment state used for this request no longer matches what "
                    f"today's continuity data would produce for fields: {sorted(stale_fields)}. "
                    f"Likely cause: bibles or an earlier clip in this location changed after "
                    f"this request was built."
                ),
                auto_repairable=True,
                repair_action="rebuild_request",
            ))

    report = _load_report(root, episode_id, scene_id, clip_id)
    visual_findings = [f for f in report.findings if f.get("tier") == "visual"]
    report.findings = [asdict(f) for f in findings] + visual_findings
    _recompute_status(report)
    _save_report(root, report)
    return report


def register_visual_qa_result(
    root: str | Path,
    episode_id: str,
    scene_id: str,
    clip_id: str,
    findings: list[dict],
    *,
    reviewed_by: str,
) -> QAReport:
    """The Tier B seam. `findings` is a list of dicts like:
    {"category": "character_drift", "severity": "error",
     "message": "...", "auto_repairable": True,
     "repair_action": "force_reference_priority", "repair_target": "char_002_amira"}

    category must be one of VISUAL_CATEGORIES -- validated, not invented.
    """
    for f in findings:
        if f.get("category") not in VISUAL_CATEGORIES:
            raise ValueError(
                f"Unknown visual QA category '{f.get('category')}'. "
                f"Must be one of {sorted(VISUAL_CATEGORIES)}."
            )

    root = Path(root)
    report = _load_report(root, episode_id, scene_id, clip_id)
    structural_findings = [f for f in report.findings if f.get("tier") == "structural"]

    new_visual = [
        asdict(QAFinding(
            check_id=f.get("check_id", f["category"]),
            category=f["category"],
            tier="visual",
            severity=f.get("severity", "error"),
            message=f["message"],
            auto_repairable=f.get("auto_repairable", False),
            repair_action=f.get("repair_action"),
            repair_target=f.get("repair_target"),
        ))
        for f in findings
    ]
    report.findings = structural_findings + new_visual
    report.reviewed_by = reviewed_by
    _recompute_status(report)
    _save_report(root, report)
    return report


def get_report(root: str | Path, episode_id: str, scene_id: str, clip_id: str) -> Optional[QAReport]:
    path = _report_path(root, episode_id, scene_id, clip_id)
    if not path.exists():
        return None
    return _load_report(root, episode_id, scene_id, clip_id)
