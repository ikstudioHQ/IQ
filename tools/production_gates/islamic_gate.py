"""
tools/production_gates/islamic_gate.py

Two layers, per the diagnosed root cause: the authoring prompt (Phase 6)
told the author what to AVOID (safety restrictions) but never gave it
anything ELIGIBLE to actually draw from -- so the author (human or
model) had nothing to cite even if it wanted to, and improvised instead.

LAYER 1 (pre-authoring): supply only eligible source excerpts, each
with its real ID, so an author has real material to quote/cite.

LAYER 2 (post-authoring): scan the finished script (including song
lyrics_theme, explicitly, per the requirement that songs get the same
rules) for patterns that make a specific Islamic-source claim. Any such
claim must carry a nearby citation ID resolving to an ELIGIBLE registry
entry. Never trusts the author to have followed instructions --
Layer 2 exists precisely because Layer 1 alone doesn't guarantee that.

This module never writes to citation_verified / scholarly_reviewed /
review_required / any approval field. Read-only against the registries,
exactly like tools/continuity/safety_check.py's existing pattern.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from tools.authoring.schemas import EpisodeScript
from tools.production_gates.islamic_sources import is_eligible, load_eligible_sources

CITATION_PATTERN = re.compile(r"\b(?:qv|dua|hd)_\d+\b")

# BLOCKER-tier claim patterns: text making a specific, attributable
# Islamic-source claim. Deliberately narrow -- ordinary expressions like
# "Alhamdulillah", "Bismillah", "Insha'Allah", "Subhanallah" are NOT
# matched here; those are everyday vocabulary, not source claims, per
# the explicit instruction not to over-block normal child-friendly
# language.
PROPHET_ATTRIBUTION = re.compile(r"\bthe prophet\b[^.!?]{0,40}\b(said|says|taught|teaches)\b", re.IGNORECASE)
ALLAH_SAYS = re.compile(r"\ballah says\b", re.IGNORECASE)
SOURCE_CATEGORY_INVOKED = re.compile(r"\b(hadith|qur['’]?an)\b", re.IGNORECASE)
DUA_ADDRESS_OPENING = re.compile(r"\bo allah\b\s*,", re.IGNORECASE)

# Known transliterated-Arabic religious-phrase markers. Honest, disclosed
# limitation: this is a curated starting list, not a language detector --
# it catches the specific real pattern found in production (a hadith's
# actual Arabic wording embedded as a song's lyrics_theme with zero
# citation) but will not catch every possible transliterated phrase.
ARABIC_MARKER_WORDS = {"sadaqa", "sadaqah", "tabassumuka", "akhika", "wajhi"}


def _find_claims(text: str) -> list[str]:
    reasons = []
    if PROPHET_ATTRIBUTION.search(text):
        reasons.append("direct Prophet attribution")
    if ALLAH_SAYS.search(text):
        reasons.append("direct Quran/Allah-says attribution")
    if SOURCE_CATEGORY_INVOKED.search(text):
        reasons.append("explicitly invokes 'hadith'/'Qur'an' as a source category")
    if DUA_ADDRESS_OPENING.search(text):
        reasons.append("dua-styled direct address to Allah")
    lowered = text.lower()
    if sum(1 for w in ARABIC_MARKER_WORDS if w in lowered) >= 1:
        reasons.append("contains transliterated-Arabic religious phrase markers")
    return reasons


def _check_text(root: Path, text: str, context: str) -> list[dict]:
    citations = CITATION_PATTERN.findall(text)

    # Citation eligibility is checked independently of claim-pattern
    # matching -- a real bug was found while testing this: text citing
    # hd_010 with plain wording (no "Prophet said"-style phrasing) was
    # slipping through because the old code only validated a citation
    # when a claim pattern ALSO matched the same text. A citation, once
    # present, must always be checked, regardless of surrounding wording.
    findings = []
    for cid in citations:
        eligible, reason = is_eligible(root, cid)
        if not eligible:
            findings.append({
                "context": context, "text": text, "cited_id": cid,
                "issue": "ineligible_or_unknown_citation",
                "message": f"Citation '{cid}' is not eligible for production use: {reason}",
                "severity": "error",
            })

    claims = _find_claims(text)
    if claims and not citations:
        findings.append({
            "context": context, "text": text, "claim_reasons": claims,
            "issue": "unsourced_religious_claim",
            "message": (
                f"Text makes an Islamic-source claim ({'; '.join(claims)}) with no citation "
                f"ID present. Never invent hadith/Qur'an/dua content -- cite a real, eligible "
                f"source ID or rewrite without the specific attribution."
            ),
            "severity": "error",
        })
    return findings


def post_authoring_islamic_check(root: str | Path, episode: EpisodeScript) -> dict:
    root = Path(root)
    findings: list[dict] = []
    for scene in episode.scenes:
        for beat in scene.get("beats", []):
            findings.extend(_check_text(root, beat.get("text", ""), f"{scene['scene_id']}/{beat['beat_id']}"))
    if episode.song:
        for field in ("lyrics_theme", "reason", "lyrics"):
            value = episode.song.get(field)
            if value:
                findings.extend(_check_text(root, value, f"song.{field}"))

    status = "BLOCKED" if any(f["severity"] == "error" for f in findings) else "PASS"
    result = {
        "episode_id": episode.episode_id, "status": status, "findings": findings,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
    out_path = root / "continuity" / "islamic_gate" / f"{episode.episode_id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def eligible_sources_prompt_block(root: str | Path) -> str:
    """LAYER 1: real, eligible source excerpts with their real IDs, to
    embed directly in the authoring prompt so the author has something
    legitimate to cite. Never includes ineligible/review-required
    entries -- an author can't cite what it was never given."""
    eligible = load_eligible_sources(root)
    if not eligible:
        return (
            "ELIGIBLE ISLAMIC SOURCES: none are currently eligible for use (all registry "
            "entries require review). Do NOT attribute any statement to the Prophet, Allah, "
            "hadith, or Qur'an, and do NOT compose a dua presented as a recited supplication. "
            "General expressions of gratitude, kindness, and everyday Islamic vocabulary "
            "(Alhamdulillah, Bismillah, Insha'Allah) are fine without citation."
        )
    lines = [
        "ELIGIBLE ISLAMIC SOURCES -- you may quote or closely paraphrase these, citing the "
        "exact ID shown (e.g. 'hd_001') inline whenever you use one. Do NOT attribute any "
        "statement to the Prophet, Allah, hadith, or Qur'an, and do NOT write a dua presented "
        "as a recited supplication, unless it is one of these exact sources with its ID cited:",
    ]
    for sid, item in sorted(eligible.items()):
        text = item.get("text_simplified") or item.get("translation") or ""
        lines.append(f"- [{sid}] {text}")
    lines.append(
        "\nGeneral expressions of gratitude, kindness, and everyday Islamic vocabulary "
        "(Alhamdulillah, Bismillah, Insha'Allah) do not need a citation."
    )
    return "\n".join(lines)
