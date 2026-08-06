"""
tools/continuity/request_serializer.py

Phase 4 requirement: the system should produce complete provider-ready
generation requests, not just prompt strings. This module is what
makes that a real file on disk rather than an in-memory object that
disappears when the process exits.

Writes to continuity/generated_requests/<episode_id>/<scene_id>/<clip_id>.json
-- deliberately separate from continuity/clip_state/ (which tracks
continuity STATE: what characters/environment/props are in this clip)
and continuity/clip_state/.../output (which tracks what a clip
PRODUCED after generation). This file is the third, distinct thing:
the actual request that was (or would be) sent to a provider, exactly
as built, including every diagnostic that was known at build time.
"""
from __future__ import annotations

import json
from pathlib import Path

from tools.continuity.request_payload_builder import ContinuityRequest
from tools.providers.base import ValidationError


def serialize_request(
    root: str | Path,
    request: ContinuityRequest,
    payload: dict,
    provider_errors: list[ValidationError],
    *,
    provider_id: str,
) -> Path:
    ctx = request.clip_context
    out_dir = (
        Path(root) / "continuity" / "generated_requests"
        / ctx["episode_id"] / ctx["scene_id"]
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{ctx['clip_id']}.json"

    provider_error_dicts = [
        {"field": e.field, "message": e.message, "severity": e.severity} for e in provider_errors
    ]
    blocked = request.has_blocking_issues() or any(e.severity == "error" for e in provider_errors)

    bundle = {
        "schema_version": "1.0",
        "provider_id": provider_id,
        "status": "BLOCKED" if blocked else "READY",
        "request": request.to_dict(),
        "provider_payload": payload if not blocked else None,
        "provider_validation": provider_error_dicts,
    }
    out_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out_path


def load_serialized_request(root: str | Path, episode_id: str, scene_id: str, clip_id: str) -> dict | None:
    path = (
        Path(root) / "continuity" / "generated_requests"
        / episode_id / scene_id / f"{clip_id}.json"
    )
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
