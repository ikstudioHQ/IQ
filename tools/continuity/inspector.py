#!/usr/bin/env python3
"""
tools/continuity/inspector.py — Continuity Inspector.

Given an episode/scene/clip, prints a human-readable report of exactly
what the continuity system knows and decided for that clip: which
characters had reference images attached, which environment/props were
text-lock-only, whether the previous clip in the thread was found,
which provider and how much of its reference-image budget got used,
and current QA status.

This reads ONLY already-saved ClipState -- it doesn't build a new
request. Run process_clip() (via ContinuityAssembler) first, then
inspect what happened.

Usage:
    python3 tools/continuity/inspector.py <episode_id> <scene_id> <clip_id> [repo_root]
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT_DEFAULT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DEFAULT))

from tools.continuity.clip_state import ClipStateRepo
from tools.continuity.reference_image_manager import ReferenceImageManager
from tools.providers.registry import get_provider


def _check(ok: bool) -> str:
    return "\u2713" if ok else "\u26a0"


def inspect(root: Path, episode_id: str, scene_id: str, clip_id: str) -> str:
    repo = ClipStateRepo(root)
    ref_mgr = ReferenceImageManager(root)

    clip = repo.load(episode_id, scene_id, clip_id)
    if clip is None:
        return (
            f"No clip_state found for {episode_id}/{scene_id}/{clip_id}.\n"
            f"Run ContinuityAssembler.process_clip() for this clip first."
        )

    lines = [f"Episode: {episode_id}", f"Scene: {scene_id}", f"Clip: {clip_id}", ""]

    lines.append("Characters:")
    used_paths = {r["path"] for r in clip.reference_images_used if r.get("role") in
                  ("primary_character", "secondary_character")}
    for cid in clip.characters_present:
        char_assets = ref_mgr.get_for_character(cid)
        has_image_attached = any(a.path in used_paths for a in char_assets)
        has_image_available = any(a.resolves_on_disk for a in char_assets)
        if has_image_attached:
            lines.append(f"  {_check(True)} {cid} (reference image attached)")
        elif has_image_available:
            lines.append(f"  {_check(False)} {cid} (image available but dropped -- over reference-image budget)")
        else:
            lines.append(f"  {_check(False)} {cid} (no reference image available -- text lock only)")
    if not clip.characters_present:
        lines.append("  (none recorded)")
    lines.append("")

    lines.append("Environment:")
    location_id = clip.environment.get("location_id")
    if location_id:
        env_assets = ref_mgr.get_for_environment(location_id)
        env_used = any(r.get("owner_id") == location_id for r in clip.reference_images_used)
        has_available = any(a.resolves_on_disk for a in env_assets)
        if env_used:
            lines.append(f"  {_check(True)} {location_id} (reference image attached)")
        elif has_available:
            lines.append(f"  {_check(False)} {location_id} (image available but dropped -- over reference-image budget)")
        else:
            lines.append(f"  {_check(False)} {location_id} (no reference image available -- text lock only)")
    else:
        lines.append("  (none recorded)")
    lines.append("")

    lines.append("Props:")
    for pid in clip.props_visible:
        prop_assets = ref_mgr.get_for_prop(pid)
        prop_used = any(r.get("owner_id") == pid for r in clip.reference_images_used)
        has_available = any(a.resolves_on_disk for a in prop_assets)
        if prop_used:
            lines.append(f"  {_check(True)} {pid} (reference image attached)")
        elif has_available:
            lines.append(f"  {_check(False)} {pid} (image available but dropped -- over reference-image budget)")
        else:
            lines.append(f"  {_check(False)} {pid} (no reference image available -- text lock only)")
    if not clip.props_visible:
        lines.append("  (none recorded)")
    lines.append("")

    lines.append("Previous Clip:")
    prev = repo.get_previous_in_thread(clip)
    if clip.previous_clip_id is None:
        lines.append("  (first clip in thread -- no previous clip expected)")
    elif prev is not None:
        lines.append(f"  {_check(True)} Loaded ({clip.previous_clip_id})")
        prev_output = prev.output or {}
        if prev_output.get("video_reference") or prev_output.get("last_frame_path"):
            lines.append(f"    lifecycle_status={prev.lifecycle_status}, "
                          f"video_reference={'set' if prev_output.get('video_reference') else 'none'}, "
                          f"last_frame_path={'set' if prev_output.get('last_frame_path') else 'none'}")
        else:
            lines.append(f"    {_check(False)} previous clip has no registered output yet -- "
                          f"run register_clip_output() after it's actually generated, "
                          f"or this clip has no real continuity anchor to build from")
    else:
        lines.append(f"  {_check(False)} previous_clip_id={clip.previous_clip_id} set, but not found in clip_state")
    lines.append("")

    lines.append("Continuation:")
    lines.append(f"  output registered: {_check(bool(clip.output))} lifecycle_status={clip.lifecycle_status}")
    lines.append("")

    lines.append("Provider:")
    lines.append(f"  {clip.provider or '(not recorded)'}")
    lines.append("")

    lines.append("Reference Image Budget:")
    try:
        provider_key = "veo-3.1-fast" if "fast" in clip.provider else "veo-3.1"
        caps = get_provider(provider_key).capabilities()
        lines.append(f"  {len(clip.reference_images_used)} / {caps.max_reference_images} used")
    except Exception:
        lines.append(f"  {len(clip.reference_images_used)} used (provider capability lookup unavailable)")
    lines.append("")

    lines.append("QA:")
    lines.append(f"  {clip.qa_status}")

    return "\n".join(lines)


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) < 3:
        print(__doc__)
        return 1
    episode_id, scene_id, clip_id = argv[0], argv[1], argv[2]
    root = Path(argv[3]).resolve() if len(argv) > 3 else ROOT_DEFAULT
    print(inspect(root, episode_id, scene_id, clip_id))
    return 0


if __name__ == "__main__":
    sys.exit(main())
