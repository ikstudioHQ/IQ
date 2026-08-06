"""
tools/continuity/id_validation.py

Phase 8 found a real BLOCKER: a nonexistent character/environment/prop
ID could reach a READY request, with the raw internal ID string leaking
into the actual prompt for characters specifically (via a silent
name-fallback in the Scene-to-Clip Bridge).

This module is the fix, placed at the correct boundary: it's called
from RequestPayloadBuilder.build() -- the one function EVERY clip must
pass through before any prompt or payload exists, regardless of
whether the SceneClipSpec came from the bridge, a test, or any future
authoring path. Fixing only the bridge would have left every other
path to build() unguarded; fixing here closes the root cause.

Validates against the canonical registries directly (continuity/
character_bible/, environment_bible/, prop_registry/) -- the same
files every other Phase 2+ component already treats as authoritative.
No new registry invented.
"""
from __future__ import annotations

from pathlib import Path


def validate_registry_ids(
    root: str | Path, *, character_ids: list[str], environment_id: str | None, prop_ids: list[str],
) -> list[dict]:
    """Returns a list of blocking diagnostic dicts (severity="error"),
    one per invalid ID found, each naming the exact ID and its type.
    Empty list means everything referenced actually exists. Never
    removes or substitutes an invalid ID -- only reports it."""
    root = Path(root)
    errors: list[dict] = []

    for cid in dict.fromkeys(character_ids):  # de-dup, preserve order
        if not (root / "continuity" / "character_bible" / f"{cid}.json").exists():
            errors.append({
                "source": "id_validation", "id_type": "character", "invalid_id": cid,
                "field": "character_ids",
                "message": (
                    f"Unknown character_id '{cid}' -- no matching entry in the Character "
                    f"Registry (continuity/character_bible/). Refusing to build a request "
                    f"that references a character that doesn't exist."
                ),
                "severity": "error",
            })

    if environment_id is not None:
        if not (root / "continuity" / "environment_bible" / f"{environment_id}.json").exists():
            errors.append({
                "source": "id_validation", "id_type": "environment", "invalid_id": environment_id,
                "field": "environment_id",
                "message": (
                    f"Unknown location_id '{environment_id}' -- no matching entry in the "
                    f"Environment Registry (continuity/environment_bible/)."
                ),
                "severity": "error",
            })

    for pid in dict.fromkeys(prop_ids):
        if not (root / "continuity" / "prop_registry" / f"{pid}.json").exists():
            errors.append({
                "source": "id_validation", "id_type": "prop", "invalid_id": pid,
                "field": "prop_ids",
                "message": (
                    f"Unknown prop_id '{pid}' -- no matching entry in the Prop Registry "
                    f"(continuity/prop_registry/)."
                ),
                "severity": "error",
            })

    return errors
