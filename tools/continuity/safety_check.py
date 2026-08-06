"""
tools/continuity/safety_check.py

Phase 1 flagged "safety and negative prompts" as claimed-but-not-found.
That was half wrong: tools/episode_consistency_check.py's
check_content_restrictions() DOES enforce phase2/data/safety/*.json --
but only against already-authored episode text files, AFTER the fact,
never against a generation request BEFORE it's sent to a provider.

This module applies the exact same structured data and the exact same
matching approach (word-boundary alias regex, citation exemption, the
sacred-entity indirect-depiction heuristic) to a clip's prompt text at
request-build time, not after. It is a new integration point for
existing rules, not a new rule -- per Phase 4's explicit instruction,
no safety rule invented here that doesn't already exist in
phase2/data/safety/*.json.

tools/episode_consistency_check.py itself is UNCHANGED. It keeps doing
its own job (auditing already-written episode text files). This is an
additive, earlier checkpoint in the pipeline, not a replacement.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

CITATION_PATTERN = re.compile(r"\b(?:qv|dua|hd)_\d+\b")
DEPICTION_WORDS = (
    "figure", "depicting", "depicts", "represents", "representing",
    "appearance of", "looks like", "shown as", "visualized as", "image of",
)
SACRED_NAMES = ("allah", "the prophet muhammad", "prophet nuh", "prophet yunus")


@dataclass(frozen=True)
class SafetyFinding:
    source: str  # "content_restrictions" | "content_scene_safety" | "sacred_depiction_heuristic"
    rule_id: str
    category: str
    level: str  # NEVER_GENERATE | BLOCK | REVIEW_REQUIRED
    matched_text: str
    message: str
    severity: str  # "error" (blocks the request) or "warning" (proceeds, flagged for review)


class SafetyChecker:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self._restrictions = self._load("phase2/data/safety/content_restrictions.json", "restrictions")
        self._safety_rules = self._load("phase2/data/safety/content_scene_safety_registry.json", "rules")

    def _load(self, rel_path: str, key: str) -> list[dict]:
        path = self.root / rel_path
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8")).get(key, [])

    def scan(self, text: str) -> list[SafetyFinding]:
        findings: list[SafetyFinding] = []
        findings.extend(self._scan_content_restrictions(text))
        findings.extend(self._scan_scene_safety(text))
        findings.extend(self._scan_sacred_depiction(text))
        return findings

    def _scan_content_restrictions(self, text: str) -> list[SafetyFinding]:
        out = []
        for r in self._restrictions:
            level = r["level"]
            if level not in ("NEVER_GENERATE", "REVIEW_REQUIRED") or not r.get("aliases"):
                continue
            pattern = re.compile(r"\b(" + "|".join(re.escape(a) for a in r["aliases"]) + r")\b", re.IGNORECASE)
            for m in pattern.finditer(text):
                window = text[max(0, m.start() - 150): m.start() + 150]
                has_citation_nearby = bool(CITATION_PATTERN.search(window))
                if has_citation_nearby and "CONTEXT_ONLY" in str(r.get("script_mention", "")):
                    continue
                out.append(SafetyFinding(
                    source="content_restrictions",
                    rule_id=r["restriction_id"],
                    category=r["category"],
                    level=level,
                    matched_text=m.group(0),
                    message=f"{r['canonical_name']}: found '{m.group(0)}' ({level}, {r['category']}) "
                            f"with no nearby citation exempting it.",
                    severity="error" if level == "NEVER_GENERATE" else "warning",
                ))
        return out

    def _scan_scene_safety(self, text: str) -> list[SafetyFinding]:
        out = []
        for r in self._safety_rules:
            if r["decision"] not in ("BLOCK", "REVIEW_REQUIRED") or not r.get("aliases"):
                continue
            pattern = re.compile(r"\b(" + "|".join(re.escape(a) for a in r["aliases"]) + r")\b", re.IGNORECASE)
            for m in pattern.finditer(text):
                out.append(SafetyFinding(
                    source="content_scene_safety",
                    rule_id=r["rule_id"],
                    category=r["category"],
                    level=r["decision"],
                    matched_text=m.group(0),
                    message=f"{r['description']} (found '{m.group(0)}')",
                    severity="error" if r["decision"] == "BLOCK" else "warning",
                ))
        return out

    def _scan_sacred_depiction(self, text: str) -> list[SafetyFinding]:
        out = []
        text_lower = text.lower()
        for name in SACRED_NAMES:
            for m in re.finditer(re.escape(name), text_lower):
                window = text_lower[max(0, m.start() - 40): m.start() + 40]
                if any(dw in window for dw in DEPICTION_WORDS):
                    out.append(SafetyFinding(
                        source="sacred_depiction_heuristic",
                        rule_id="indirect_sacred_entity_depiction",
                        category="SACRED_ENTITY_DEPICTION",
                        level="NEVER_GENERATE",
                        matched_text=name,
                        message=f"'{name}' appears near a depiction word ({window.strip()}) -- possible "
                                f"indirect visual depiction request. Human review recommended even if "
                                f"this is a false positive.",
                        severity="error",
                    ))
        return out
