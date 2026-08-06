"""
tools/production_gates/islamic_sources.py

Shared loader for the three Islamic source registries. Read-only,
never mutates citation_verified / scholarly_reviewed / review_required
/ approval fields -- those are the repository's own authority, this
module only reads them.

ELIGIBLE = review_required is False AND is_disputed is not True. This
uses the repository's own existing fields at face value -- no new
theology policy invented. hd_010 (used prominently in the audited
production run despite review_required=True) is correctly NOT eligible
under this definition, which is exactly the gap that let it through.
"""
from __future__ import annotations

import json
from pathlib import Path

SOURCE_FILES = {
    "hd": ("phase2/data/islamic/hadith.json", "hadith_entries", "hadith_id"),
    "dua": ("phase2/data/islamic/duas.json", "duas", "dua_id"),
    "qv": ("phase2/data/islamic/quran_verses.json", "verses", "verse_id"),
}


def load_all_sources(root: str | Path) -> dict:
    """All entries, keyed by their real ID, regardless of eligibility --
    used to distinguish 'cites a nonexistent ID' from 'cites a real but
    ineligible ID', which need different diagnostics."""
    root = Path(root)
    all_sources: dict = {}
    for prefix, (relpath, listkey, idkey) in SOURCE_FILES.items():
        path = root / relpath
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for item in data.get(listkey, []):
            sid = item.get(idkey)
            if sid:
                all_sources[sid] = item
    return all_sources


def load_eligible_sources(root: str | Path) -> dict:
    all_sources = load_all_sources(root)
    return {
        sid: item for sid, item in all_sources.items()
        if item.get("review_required") is False and item.get("is_disputed") is not True
    }


def is_eligible(root: str | Path, source_id: str) -> tuple[bool, str]:
    """Returns (eligible, reason). reason explains why not, if not."""
    all_sources = load_all_sources(root)
    if source_id not in all_sources:
        return False, f"'{source_id}' does not match any entry in the repository's Islamic source registries"
    item = all_sources[source_id]
    if item.get("is_disputed") is True:
        return False, f"'{source_id}' is marked is_disputed=true in the registry"
    if item.get("review_required") is not False:
        return False, f"'{source_id}' has review_required={item.get('review_required')} -- not yet cleared"
    return True, ""
