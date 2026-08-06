"""
tools/continuity/clip_output_registrar.py

This system does not call the Veo API itself yet (that's a deliberate
Phase 2/3 boundary -- see Phase 2 architecture doc, "Provider Adapter
... does NOT call any external API this phase"). Clips get generated
by a human running the built payload through Veo, or eventually by an
orchestrator. Either way, SOMETHING needs to tell the continuity system
"this clip is done, here's what it actually produced" -- that's what
register_clip_output() is for. Without it, ClipState.output stays
empty forever and Last Frame Continuity has nothing to read.

This is the one deliberately manual seam in an otherwise automated
foundation, until Phase 7 (or whenever real API calling is approved)
closes the loop.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from tools.continuity.clip_state import ClipStateRepo
from tools.providers.base import ProviderCapabilities


def register_clip_output(
    root: str | Path,
    episode_id: str,
    scene_id: str,
    clip_id: str,
    *,
    provider_capabilities: ProviderCapabilities,
    video_reference: Optional[str] = None,
    last_frame_path: Optional[str] = None,
    generated_at: Optional[datetime] = None,
) -> dict:
    """Records what a clip actually produced. Call this after running the
    built payload through Veo (or whatever provider) and, ideally, after
    extracting the clip's final frame to `last_frame_path`.

    video_reference: the provider's own stored video object/URI, needed
    ONLY for true video-extension continuation. Subject to the
    provider's video_retention_days -- this function computes and stores
    the expiry so the Request Payload Builder can check it later without
    re-deriving the math.

    last_frame_path: a plain extracted image file. Not subject to the
    provider's video retention window (it's just an image on disk), so
    this remains usable for first-frame/image-to-video continuation even
    after the source video itself has expired on the provider's servers.
    """
    repo = ClipStateRepo(root)
    clip = repo.load(episode_id, scene_id, clip_id)
    if clip is None:
        raise ValueError(
            f"No clip_state found for {episode_id}/{scene_id}/{clip_id}. "
            f"Run ContinuityAssembler.process_clip() to plan the clip before "
            f"registering its output."
        )

    generated_at = generated_at or datetime.now(timezone.utc)
    retention_expires_at = None
    if video_reference:
        retention_expires_at = (
            generated_at + timedelta(days=provider_capabilities.video_retention_days)
        ).isoformat()

    clip.output = {
        "video_reference": video_reference,
        "last_frame_path": last_frame_path,
        "generated_at": generated_at.isoformat(),
        "video_retention_expires_at": retention_expires_at,
    }
    clip.lifecycle_status = "GENERATED"
    repo.save(clip)
    return clip.output


def video_extension_still_valid(output: dict, *, now: Optional[datetime] = None) -> bool:
    """Whether a previously-registered video_reference is still within the
    provider's retention window and can be used for true video extension.
    Returns False (not an error) once expired -- callers should fall back
    to last_frame_path continuation instead, per the Phase 2 architecture
    doc's stated preference for still-frame continuity as the robust
    default."""
    expires_at = output.get("video_retention_expires_at")
    if not output.get("video_reference") or not expires_at:
        return False
    now = now or datetime.now(timezone.utc)
    return datetime.fromisoformat(expires_at) > now
