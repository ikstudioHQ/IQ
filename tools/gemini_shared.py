"""Shared, format-independent logic reused by BOTH the frozen song
compiler (compile_gemini_scenes.py, NOT modified by this file) and the
new episode compiler. Extracted here so future changes to shared rules
(dependency-stripping, safety scanning, traceability hashing) happen
once, not duplicated and drifted across two compilers."""
import re, hashlib, json, os

EXTERNAL_DEP_PATTERNS = re.compile(
    r"\.md\b|\.json\b|per (this )?repository|see file|refer to|according to file|"
    r"per music_notes|per sound_effects|per lyrics|use canonical prompt|use previous file|"
    r"follow repository|as defined elsewhere",
    re.IGNORECASE)
SCAFFOLD_PATTERNS = re.compile(
    r"6-VIEW|TURNAROUND PROMPT|REFERENCE SHEET|CHARACTER SHEET|PROMPT TEMPLATE|BLOCK \d|"
    r"PROVENANCE|APPENDIX|SOURCE FILE|NOTES FOR|FILE:|SECTION:",
    re.IGNORECASE)

def check_text_integrity(text):
    """Real, GENERALIZED check -- built after finding that regression
    tests only checked for specific already-seen bad strings, never
    for the CLASS of defect (stripper leaving grammatically broken
    text behind). Catches the pattern regardless of which word/filename
    triggered it, not just the exact strings already found."""
    issues = []
    if re.search(r"\s+\.(?!\.)", text):
        issues.append("space directly before a period (likely a stripped parenthetical left a gap between a word and its real sentence-ending period)")
    if re.search(r"(?:^|\s)(in|the|a|an|of|for|with|to|and)\s*,\s", text):
        issues.append("dangling preposition/article before comma (likely a stripped reference left a gap)")
    if re.search(r"  +", text):
        issues.append("double space (likely a stripped reference collapsed poorly)")
    contractions = {"it's", "that's", "what's", "let's", "there's", "here's", "who's", "he's", "she's"}
    for m in re.finditer(r"\b(\w+)'s\s*(\.(?!\.\.))(?!\.)", text):
        if m.group(1).lower() not in contractions:
            issues.append("dangling possessive with nothing following (likely a stripped reference)")
            break
    if re.search(r"(?:^|\s)(in|from|the)\s*\.\s", text):
        issues.append("dangling preposition/article before a sentence-ending period")
    if re.search(r"\s,\s*,", text):
        issues.append("doubled comma (likely two adjacent strips)")
    return issues

def strip_dependencies(prompt):
    """The real, structurally-fixed stripper. v2.50 fix: consumes a
    trailing possessive 's so it never leaves dangling grammar; v2.50
    also collapses the resulting double space. v2.57 fix (found by
    real diagnosis): the possessive-consuming pattern required a
    literal space after 's ("'s "), but real source text sometimes
    wraps mid-phrase ("ending_styles.json's\\ndua_close style"),
    putting a newline there instead -- \\s now used instead of a
    literal space so it matches either."""
    for _ in range(3):
        if not EXTERNAL_DEP_PATTERNS.search(prompt):
            break
        prompt = re.sub(r",?\s*per\s+[\w/.]+\.(md|json)(?:'s\s+[\w\s-]+)?", "", prompt, flags=re.IGNORECASE)
        prompt = re.sub(r"[\w/.-]*[\w/-]+\.(md|json)'s\b", "", prompt, flags=re.IGNORECASE)
        prompt = re.sub(r"[\w/.-]*[\w/-]+\.(md|json)\b", "", prompt, flags=re.IGNORECASE)
        prompt = re.sub(r"  +", " ", prompt)
    return prompt

def strip_scaffold(text):
    return "\n".join(l for l in text.split("\n") if not SCAFFOLD_PATTERNS.search(l))

def parse_dialogue(text):
    lines = re.findall(r"^([A-Z][A-Z\s]+):\s*(.+)$", text, re.MULTILINE)
    return [{"speaker": s.strip(), "line": l.strip()} for s, l in lines]

def compute_content_hash(*texts):
    h = hashlib.sha256()
    for t in texts:
        h.update(t.encode("utf-8"))
    return h.hexdigest()[:16]

def truncate_at_sentence(text, max_chars=700):
    """Real fix (v2.62): the em-dash fallback was WRONG -- an em-dash
    marks clause continuation, not a sentence boundary, so cutting
    there mid-thought produced exactly the confirmed real defect
    ('Depth of field: Medium —' with nothing after). Only a real
    period-space is a valid sentence boundary; the word-boundary
    fallback below already handles the no-period case safely."""
    if len(text) <= max_chars:
        return text
    window = text[:max_chars]
    last_period = window.rfind(". ")
    if last_period > max_chars * 0.4:
        return text[:last_period + 1].rstrip()
    return window.rsplit(" ", 1)[0].rstrip() + "."
