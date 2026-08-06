"""
tools/production_gates/duration_gate.py

Root cause of Blocker 1 (confirmed by direct inspection): the authoring
prompt told the author "TARGET DURATION: approximately N minutes" as
prose, but nothing downstream ever measured or enforced it. An episode
with ~46 clips (~6.1 real minutes at Veo's actual forced 8s/clip) was
silently accepted as satisfying a 10-minute request because no gate
existed to check.

This measures REAL planned production time -- clip count times the
actual provider-forced clip duration -- not word count, not a rough
guess. It reuses the Scene-to-Clip Bridge (unchanged) to get the real
clip count for a given episode + provider, so this gate can never
drift out of sync with what the bridge would actually produce.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from tools.authoring.scene_to_clip_bridge import build_clip_specs
from tools.authoring.schemas import EpisodeScript
from tools.providers.base import ProviderCapabilities

DEFAULT_TOLERANCE = 0.15  # +/-15%: generous enough not to demand exact
# runtime (real dialogue/action pacing always varies a little), tight
# enough that the ~37-39% shortfall actually found in production would
# have been caught immediately (well outside this band).


def measure_planned_duration(root, episode, provider_capabilities):
    specs, diagnostics = build_clip_specs(root, episode, provider_capabilities)
    clip_seconds = provider_capabilities.max_duration_seconds(using_reference_images=True)
    planned_seconds = len(specs) * clip_seconds
    return {
        "clip_count": len(specs),
        "provider_clip_seconds": clip_seconds,
        "planned_seconds": planned_seconds,
        "bridge_diagnostics": diagnostics,
    }


def duration_gate_check(root, episode, provider_capabilities, requested_minutes, tolerance=DEFAULT_TOLERANCE):
    root = Path(root)
    measured = measure_planned_duration(root, episode, provider_capabilities)
    requested_seconds = requested_minutes * 60
    deviation_ratio = (measured["planned_seconds"] - requested_seconds) / requested_seconds if requested_seconds else 0.0

    if deviation_ratio < -tolerance:
        status = "TOO_SHORT"
    elif deviation_ratio > tolerance:
        status = "TOO_LONG"
    else:
        status = "PASS"

    result = {
        "episode_id": episode.episode_id,
        "requested_minutes": requested_minutes,
        "requested_seconds": requested_seconds,
        "planned_seconds": measured["planned_seconds"],
        "planned_minutes": round(measured["planned_seconds"] / 60, 2),
        "clip_count": measured["clip_count"],
        "provider_clip_seconds": measured["provider_clip_seconds"],
        "deviation_ratio": round(deviation_ratio, 4),
        "tolerance": tolerance,
        "status": status,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }

    out_path = root / "continuity" / "duration_gate" / f"{episode.episode_id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def build_expansion_request(root, episode, gate_result):
    """A real, usable prompt for the author (live or manual) to expand
    or condense the episode to hit the target -- explicit that this
    must come from real added/removed story content, never padding."""
    if gate_result["status"] == "TOO_SHORT":
        deficit_seconds = gate_result["requested_seconds"] - gate_result["planned_seconds"]
        direction = "EXPAND"
        instruction = (
            f"This episode is {gate_result['planned_minutes']} minutes "
            f"(target: {gate_result['requested_minutes']} minutes) -- short by "
            f"approximately {round(deficit_seconds)} seconds "
            f"(~{round(deficit_seconds / gate_result['provider_clip_seconds'])} more clips worth of real content).\n\n"
            f"Add genuine additional story material -- new scenes, new beats, deeper "
            f"character moments, or more developed dialogue -- to close this gap.\n\n"
            f"Do NOT pad with: repeated dialogue, artificial pauses, duplicated scenes, "
            f"an unnecessary song, or filler action beats that don't advance the story. "
            f"If the story genuinely doesn't need to be longer, say so explicitly rather "
            f"than padding it."
        )
    else:
        surplus_seconds = gate_result["planned_seconds"] - gate_result["requested_seconds"]
        direction = "CONDENSE"
        instruction = (
            f"This episode is {gate_result['planned_minutes']} minutes "
            f"(target: {gate_result['requested_minutes']} minutes) -- long by "
            f"approximately {round(surplus_seconds)} seconds.\n\n"
            f"Tighten pacing and cut what's least essential to the story. Do NOT blindly "
            f"truncate the episode wherever it currently ends -- decide deliberately what "
            f"can be shortened or removed while keeping the story coherent and complete."
        )

    return "\n".join([
        f"EPISODE DURATION {direction} REQUIRED",
        f"episode_id: {episode.episode_id}",
        f"title: {episode.title}",
        "",
        instruction,
        "",
        "Return the full corrected EpisodeScript JSON in the same schema as before.",
    ])
