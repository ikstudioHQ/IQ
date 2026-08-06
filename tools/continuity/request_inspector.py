#!/usr/bin/env python3
"""
tools/continuity/request_inspector.py — Request Inspector.

Distinct from tools/continuity/inspector.py (the Continuity Inspector,
which reports on continuity STATE -- characters/environment/props for
a clip). This one reports on a serialized REQUEST -- the actual
provider-ready generation request built for a clip, its safety
findings, its diagnostics, and whether it's actually ready to send.

Usage:
    python3 tools/continuity/request_inspector.py <episode_id> <scene_id> <clip_id> [repo_root]
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT_DEFAULT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DEFAULT))

from tools.continuity.request_serializer import load_serialized_request


def inspect_request(root: Path, episode_id: str, scene_id: str, clip_id: str) -> str:
    bundle = load_serialized_request(root, episode_id, scene_id, clip_id)
    if bundle is None:
        return (
            f"No serialized request found for {episode_id}/{scene_id}/{clip_id}.\n"
            f"Run ContinuityAssembler.process_clip() for this clip first."
        )

    req = bundle["request"]
    lines = [
        f"Episode: {episode_id}", f"Scene: {scene_id}", f"Clip: {clip_id}", "",
        f"Provider: {bundle['provider_id']}",
        f"Status: {bundle['status']}",
        "",
        f"Prompt ({len(req['prompt'])} chars):",
        f"  {req['prompt'][:200]}{'...' if len(req['prompt']) > 200 else ''}",
        "",
        f"Negative constraints ({len(req['negative_constraints'])}):",
    ]
    for c in req["negative_constraints"]:
        lines.append(f"  - {c}")
    lines.append("")

    lines.append(f"Reference images ({len(req['reference_images'])}):")
    for img in req["reference_images"]:
        lines.append(f"  - {img['owner_id']} [{img['role']}] -> {img['path']}")
    if req.get("dropped_reference_notes"):
        lines.append(f"  Dropped ({len(req['dropped_reference_notes'])}):")
        for d in req["dropped_reference_notes"]:
            lines.append(f"    - {d}")
    lines.append("")

    lines.append(f"Continuation: mode={req['continuation_mode']}, "
                 f"anchor={req['previous_frame_image']}")
    lines.append("")

    lines.append(f"Environment: {req['environment_metadata']} "
                 f"(provenance: {req['environment_provenance']})")
    lines.append("")

    lines.append(f"Generation settings: {req['generation_settings']}")
    lines.append("")

    findings = req.get("safety_findings", [])
    lines.append(f"Safety findings ({len(findings)}):")
    if not findings:
        lines.append("  (none)")
    for f in findings:
        marker = "BLOCKING" if f["severity"] == "error" else "review"
        lines.append(f"  [{marker}] {f['rule_id']} ({f['category']}): {f['message']}")
    lines.append("")

    diags = req.get("diagnostics", [])
    lines.append(f"Diagnostics ({len(diags)}):")
    if not diags:
        lines.append("  (none)")
    for d in diags:
        marker = "BLOCKING" if d["severity"] == "error" else "note"
        lines.append(f"  [{marker}] {d['field']}: {d['message']}")
    lines.append("")

    prov_errs = bundle.get("provider_validation", [])
    lines.append(f"Provider validation ({len(prov_errs)}):")
    if not prov_errs:
        lines.append("  (none)")
    for e in prov_errs:
        marker = "BLOCKING" if e["severity"] == "error" else "note"
        lines.append(f"  [{marker}] {e['field']}: {e['message']}")
    lines.append("")

    if bundle["status"] == "READY":
        lines.append(f"Provider payload: {len(str(bundle['provider_payload']))} chars, ready to send.")
    else:
        lines.append("Provider payload: NOT built -- blocking issues above must be resolved first.")

    return "\n".join(lines)


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) < 3:
        print(__doc__)
        return 1
    episode_id, scene_id, clip_id = argv[0], argv[1], argv[2]
    root = Path(argv[3]).resolve() if len(argv) > 3 else ROOT_DEFAULT
    print(inspect_request(root, episode_id, scene_id, clip_id))
    return 0


if __name__ == "__main__":
    sys.exit(main())
