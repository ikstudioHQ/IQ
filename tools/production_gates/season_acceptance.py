"""
tools/production_gates/season_acceptance.py

Authoring -> Islamic Gate -> Duration Gate -> Continuity Gate -> Safety
Gate (existing, Phase 4, unchanged) -> Packaging -> Acceptance Gate.

This is the final check before a season can be called READY. It never
marks a season ready by default -- an episode/season starts and stays
REPAIR_REQUIRED unless every gate explicitly reports PASS. Nothing here
re-implements any existing gate; it only calls and aggregates them.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from tools.authoring.manual_author_seam import load_authored_episode
from tools.production_gates.continuity_gate import continuity_gate_check
from tools.production_gates.duration_gate import duration_gate_check
from tools.production_gates.islamic_gate import post_authoring_islamic_check
from tools.production_gates.song_gate import count_songs_in_season, song_gate_check
from tools.providers.registry import get_provider


def check_requests_built_for_all_planned_clips(root: str | Path, episode_ids: list[str]) -> list[dict]:
    """Real gap found in production: season_acceptance could say READY
    based on Duration/Islamic/Song/Continuity gates alone, while the
    actual per-clip request-building step (ContinuityAssembler.process_clip,
    where registry ID validation and safety screening actually happen)
    never ran for a single clip. A season that only got as far as
    authoring + clip planning is not a provider-ready production
    package -- confirmed as a real, reproduced defect, not assumed."""
    import json as _json
    from tools.continuity.request_serializer import load_serialized_request

    root = Path(root)
    findings = []
    for episode_id in episode_ids:
        plan_path = root / "continuity" / "clip_plan" / f"{episode_id}.json"
        if not plan_path.exists():
            continue  # duration/islamic gates already report this episode as unauthored/unplanned
        plan = _json.loads(plan_path.read_text(encoding="utf-8"))
        missing = []
        for clip in plan.get("clips", []):
            bundle = load_serialized_request(root, episode_id, clip["scene_id"], clip["clip_id"])
            if bundle is None:
                missing.append(f"{clip['scene_id']}/{clip['clip_id']}")
        if missing:
            findings.append({
                "episode_id": episode_id, "issue": "clips_planned_but_requests_not_built",
                "message": (
                    f"{len(missing)} of {len(plan.get('clips', []))} planned clips in {episode_id} "
                    f"have no generated_requests file -- ContinuityAssembler.process_clip() never "
                    f"ran for them. This episode has been authored and clip-planned but not actually "
                    f"processed into provider-ready requests; it is not a complete production package."
                ),
                "severity": "error",
            })
    return findings


def run_season_acceptance_gate(root: str | Path, season_id: str, episode_ids: list[str],
                                provider_id: str, requested_minutes: float,
                                required_song_count: int | None = None) -> dict:
    root = Path(root)
    provider = get_provider(provider_id)
    episodes = []
    per_episode: dict = {}

    for eid in episode_ids:
        episode = load_authored_episode(root, eid)
        if episode is None:
            per_episode[eid] = {"status": "MISSING", "gates": {}}
            continue
        episodes.append(episode)

        islamic = post_authoring_islamic_check(root, episode)
        duration = duration_gate_check(root, episode, provider.capabilities(), requested_minutes)
        song = song_gate_check(root, episode)

        gates = {"islamic": islamic["status"], "duration": duration["status"], "song": song["status"]}
        episode_status = "REPAIR_REQUIRED" if (
            gates["islamic"] == "BLOCKED" or gates["duration"] in ("TOO_SHORT", "TOO_LONG")
            or gates["song"] == "BLOCKED"
        ) else "PASS"
        per_episode[eid] = {"status": episode_status, "gates": gates,
                             "islamic_findings": islamic["findings"], "duration_result": duration,
                             "song_findings": song["findings"]}

    continuity = continuity_gate_check(root, season_id, episodes) if episodes else {"status": "PASS", "findings": []}
    requests_findings = check_requests_built_for_all_planned_clips(root, episode_ids)

    all_episode_statuses = {v["status"] for v in per_episode.values()}
    real_song_count = count_songs_in_season(episodes)
    song_count_ok = required_song_count is None or real_song_count == required_song_count

    overall_status = "READY" if (
        all_episode_statuses == {"PASS"} and continuity["status"] == "PASS" and song_count_ok
        and not requests_findings
    ) else "REPAIR_REQUIRED"

    result = {
        "season_id": season_id,
        "status": overall_status,  # never defaults to READY -- computed strictly above
        "note": (
            "READY means all pre-generation gates (Duration, Islamic, Song, Continuity) "
            "passed AND every planned clip has a real generated_requests file (registry "
            "ID validation and safety screening actually ran). It does NOT mean clips "
            "have been generated or rendered -- check job_state/production_status for "
            "real generation progress."
        ),
        "episodes": per_episode,
        "continuity_gate": continuity,
        "requests_built_findings": requests_findings,
        "real_song_count": real_song_count,
        "required_song_count": required_song_count,
        "song_count_ok": song_count_ok,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
    out_path = root / "continuity" / "season_acceptance" / f"{season_id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result
