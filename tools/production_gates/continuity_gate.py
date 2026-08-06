"""
tools/production_gates/continuity_gate.py

Runs across ALL episodes of a season together, not per-episode --
catches problems no single-episode check can see: a thread referenced
before it's ever created, invalid registry IDs anywhere in the season,
and duplicate/near-duplicate thread declarations that suggest the
story forgot it already established something (a soft signal, not a
hard fail -- text-similarity heuristics are too unreliable to block on).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from tools.authoring.schemas import EpisodeScript
from tools.continuity.id_validation import validate_registry_ids


def check_thread_reference_ordering(episodes_in_order):
    """Root-cause fix for a confirmed real defect: this used to
    independently re-simulate StoryStateRepo's thread_id assignment
    formula (a per-episode enumerate() index) instead of using
    StoryStateRepo itself. StoryStateRepo actually assigns IDs from
    len(state.threads) -- a running count across the WHOLE SEASON, not
    reset per episode. The two formulas only coincide for episode 1;
    from episode 2 onward they diverge, so the gate was validating
    references against IDs that don't match what the real system
    actually produces -- a false-PASS pathway, confirmed reproducible
    with real production content.

    Fixed by never re-implementing the ID algorithm a second time:
    apply every episode's story_updates through a REAL, isolated
    StoryStateRepo (a throwaway temp directory, never touching the
    caller's actual season data) in the same order production would,
    and check references against the ACTUAL resulting thread IDs.
    Single source of truth -- this can't drift again because there is
    only one implementation of the ID algorithm left to drift."""
    import tempfile
    from tools.authoring.story_state import StoryStateRepo

    findings = []
    with tempfile.TemporaryDirectory() as tmp:
        repo = StoryStateRepo(tmp)
        season_id = "continuity_gate_dry_run"
        for ep in episodes_in_order:
            updates = ep.story_updates or {}
            state_before = repo.load(season_id)
            existing_ids = {t["thread_id"] for t in state_before.threads}
            for ref_id in updates.get("referenced_thread_ids", []) + updates.get("resolved_thread_ids", []):
                if ref_id not in existing_ids:
                    findings.append({
                        "episode_id": ep.episode_id, "thread_id": ref_id,
                        "issue": "thread_referenced_before_created",
                        "message": (
                            f"Episode {ep.episode_id} references/resolves thread '{ref_id}' but the "
                            f"real Story State system (StoryStateRepo) never actually created a thread "
                            f"with that ID from any earlier episode. Verified against the real ID "
                            f"assignment algorithm, not a re-simulation of it."
                        ),
                        "severity": "error",
                    })
            repo.apply_episode_updates(season_id, ep.episode_id, updates)
    return findings


def check_duplicate_characters_within_thread(episodes):
    """New check, added after a real example was found in production:
    validate_registry_ids only confirms an ID EXISTS -- it cannot catch
    the same real character ID appearing twice in one thread's
    involved_characters (e.g. a thread meant to involve two different
    characters that ended up pointing at the same character ID twice,
    likely because one of the two never got its own registry entry).
    This is a data-quality signal, not a hard existence failure --
    warning, not blocking, since the IDs themselves are all valid."""
    findings = []
    for ep in episodes:
        for new_thread in (ep.story_updates or {}).get("new_threads", []):
            involved = new_thread.get("involved_characters", [])
            seen = set()
            dupes = {c for c in involved if c in seen or seen.add(c)}
            for cid in dupes:
                findings.append({
                    "episode_id": ep.episode_id, "issue": "duplicate_character_in_thread",
                    "message": (
                        f"Episode {ep.episode_id}'s new '{new_thread['kind']}' thread "
                        f"(\"{new_thread['description'][:60]}...\") lists character '{cid}' more than "
                        f"once in involved_characters. All IDs are individually valid, so registry "
                        f"validation alone cannot catch this -- likely a different intended character "
                        f"was meant here and either shares an ID by mistake or was never registered."
                    ),
                    "severity": "warning",
                })
    return findings


def check_season_wide_registry_ids(root, episodes):
    findings = []
    for ep in episodes:
        for scene in ep.scenes:
            errors = validate_registry_ids(
                root,
                character_ids=scene.get("characters_present", []),
                environment_id=scene.get("location_id"),
                prop_ids=scene.get("props_visible", []),
            )
            for e in errors:
                e["episode_id"] = ep.episode_id
                e["scene_id"] = scene["scene_id"]
                findings.append(e)
    return findings


def check_duplicate_thread_declarations(episodes):
    findings = []
    seen = {}
    for ep in episodes:
        for new_thread in (ep.story_updates or {}).get("new_threads", []):
            key = (new_thread["kind"], new_thread["description"].strip().lower())
            if key in seen:
                findings.append({
                    "episode_id": ep.episode_id, "issue": "possible_duplicate_thread",
                    "message": (
                        f"Episode {ep.episode_id} declares a new '{new_thread['kind']}' thread "
                        f"with text identical to one already declared in {seen[key]} -- possible "
                        f"accidental re-introduction of an already-established thread."
                    ),
                    "severity": "warning",
                })
            else:
                seen[key] = ep.episode_id
    return findings


def continuity_gate_check(root, season_id, episodes):
    root = Path(root)
    findings = (
        check_thread_reference_ordering(episodes)
        + check_season_wide_registry_ids(root, episodes)
        + check_duplicate_thread_declarations(episodes)
        + check_duplicate_characters_within_thread(episodes)
    )
    status = "BLOCKED" if any(f["severity"] == "error" for f in findings) else "PASS"
    result = {
        "season_id": season_id, "status": status, "episode_count": len(episodes),
        "findings": findings, "checked_at": datetime.now(timezone.utc).isoformat(),
    }
    out_path = root / "continuity" / "continuity_gate" / f"{season_id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result
