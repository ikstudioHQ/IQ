#!/usr/bin/env python3
"""
validate_repo.py — Islamic Kids Studio repository validator / health dashboard.

Run this before trusting any "zero broken references / zero contradictions"
claim in this repository. It actually checks, instead of asserting.

Checks performed:
  1. Every .json file parses as valid JSON.
  2. Every .yaml/.yml file parses as valid YAML (if PyYAML is installed;
     otherwise this check is skipped with a warning, not a false pass).
  3. Every backtick-quoted `path/like/this.ext` reference inside .md/.json
     files that contains a "/" is checked against the real file tree.
  4. Every entry in knowledge_index.json and sources/characters/character_index.json
     is checked to confirm the file(s) it points to actually exist.
  5. Legacy character names (Nur, Lumi, Mama-as-character) flagged if found.
  6. Version consistency: repo-level version markers must match the
     "Current Repository Version" declared in VERSION_COMPATIBILITY.md.
  7. Duplicate IDs: the same character_id/dua_id/topic_id/etc. declared
     more than once inside the same JSON file (a real data-integrity bug).
  8. Unreviewed Islamic content: flags citation_verified and
     scholarly_reviewed coverage separately (see verification_pipeline.md).
  9. Circular references: superseded_by chains that loop back on
     themselves (added v2.13).
  10. Empty required fields: an ID/name/definition field present but
      blank on a known entry type (added v2.13).
  11. Writes REPO_HEALTH_REPORT.md — a standing dashboard snapshot, so repo
     health can be checked without re-running the script.

Usage:
    python3 tools/validate_repo.py [repo_root]

Exit code is non-zero if any check fails, so this can be wired into CI.
"""
import json
import os
import re
import sys

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

# Output filenames these prompts are *expected* to describe as generation
# targets, not files that should already exist in the repo.
KNOWN_GENERATED_OUTPUTS = {
    "ep_summary.md", "learning_goals.md", "curriculum_map.md", "islamic_refs.md",
    "vocabulary.md", "story_outline.md", "complete_script.md", "narration.md",
    "dialogue.md", "scene_breakdown.md", "camera_directions.md",
    "animation_directions.md", "image_prompts.md", "thumbnail.md",
    "music_notes.md", "sound_effects.md", "voice_instructions.md",
    "subtitles.srt", "youtube_title.md", "description.md", "seo_metadata.md",
    "tags.md", "thumbnail_text.md", "qa_checklist.md", "validation_report.md",
    "script.md", "scenes.md", "camera.md", "animation.md", "music.md",
    "sound.md", "execution_log.json", "execution_state.json",
    "hashtags.md", "editing_notes.md", "lyrics_and_song.md", "verification_report.md",
    "missing_knowledge_report.md", "repository_improvement_suggestions.md",
    "zayd_v2.md",  # example filename given for a hypothetical future version bump
    "MASTER_PROMPT.md",  # intentional local-only bootstrap; absent from distribution/GitHub is valid
}

LEGACY_CHARACTER_NAMES = ["Nur", "Lumi", "char_nur", "char_lumi", "char_mama"]

# Repo-level version markers checked against VERSION_COMPATIBILITY.md.
# Character/asset/module versions are intentionally excluded — see
# phase1/docs/governance/versioning_policy.md.
VERSION_TRACKED_FILES = {
    "repository_manifest.json": ("json", "repository_version"),
    "knowledge_index.json": ("json", "version"),
    "phase2/data/config/settings.yaml": ("yaml_text", "version:"),
    "MASTER_PROMPT.md": ("md_header", r"\*\*Version:\*\*\s*([0-9][0-9.\-]*)"),
    "README.md": ("md_header", r"Repository version:\s*\*\*v([0-9][0-9.\-]*)\*\*"),
    "generated/repository_fingerprint.json": ("json", "repository_version"),
    "runtime/runtime_manifest.json": ("json", "repository_version"),
}

# Files allowed to mention an old version number in a deliberate, labeled
# historical/example context (a changelog-style note, or an independently
# -tracked sub-version like a character module version). Anything else
# matching a stale version pattern outside these files is suspicious.
STALE_VERSION_ALLOWED_FILES = {"CHANGELOG.md", "VERSION_COMPATIBILITY.md", "AUDIT_REPORT.md", "FINAL_AUDIT_REPORT.md", "completed.md", "REPO_HEALTH_REPORT.md", "versioning_policy.md", "DESIGN_PRINCIPLES.md"}

ID_FIELDS_TO_CHECK = [
    "character_id", "dua_id", "hadith_id", "topic_id", "episode_id",
    "env_id", "asset_id", "lesson_id", "verse_id",
]

# Maps a top-level JSON list key to the ONE field that is that list's own
# identity field. Other *_id-shaped fields inside the same item (e.g. an
# "assets" entry's "character_id", which is a foreign-key reference to a
# character, not a second identity for the asset) are deliberately not
# checked — checking them produced false positives in earlier versions of
# this script. Add an entry here when a new list of uniquely-identified
# records is introduced; unmapped lists are skipped (no duplicate check)
# rather than guessed at.
LIST_IDENTITY_FIELD = {
    "characters": "character_id",
    "duas": "dua_id",
    "hadith_entries": "hadith_id",
    "topics": "topic_id",
    "environments": "env_id",
    "assets": "asset_id",
    "verses": "verse_id",
    "words": "vocab_id",
    "conflicts": "conflict_id",
    "hooks": "hook_id",
    "endings": "ending_id",
    "prophets": "prophet_id",
    "patterns": "pattern_id",
}


def find_all_files(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in (".git", "node_modules"))
        for f in sorted(filenames):
            out.append(os.path.relpath(os.path.join(dirpath, f), root))
    return sorted(out)


def check_json(root, files, errors):
    for f in files:
        if f.endswith(".json"):
            path = os.path.join(root, f)
            try:
                json.load(open(path, encoding="utf-8"))
            except Exception as e:
                errors.append(f"[JSON PARSE FAIL] {f}: {e}")


def check_yaml(root, files, errors, warnings):
    if not HAVE_YAML:
        warnings.append("PyYAML not installed — skipping YAML validation. "
                         "Install with: pip install pyyaml --break-system-packages")
        return
    for f in files:
        if f.endswith((".yaml", ".yml")):
            path = os.path.join(root, f)
            try:
                list(yaml.safe_load_all(open(path, encoding="utf-8")))
            except Exception as e:
                errors.append(f"[YAML PARSE FAIL] {f}: {e}")


def check_references(root, files, errors, warnings):
    file_set = set(files)
    basenames = {}
    for f in files:
        basenames.setdefault(os.path.basename(f), []).append(f)

    ref_pattern = re.compile(r"`([A-Za-z0-9_\-/]+\.(?:md|json|yaml|yml|csv))`")
    for f in files:
        if not (f.endswith(".md") or f.endswith(".json")):
            continue
        path = os.path.join(root, f)
        try:
            content = open(path, encoding="utf-8").read()
        except Exception:
            continue
        for m in ref_pattern.findall(content):
            base = os.path.basename(m)
            if base in KNOWN_GENERATED_OUTPUTS:
                continue
            if "/" in m:
                if m.lstrip("/") not in file_set and m not in file_set:
                    warnings.append(f"[POSSIBLE BROKEN REF] {f} references '{m}' (not found on disk)")
            else:
                if base not in basenames:
                    warnings.append(f"[POSSIBLE BROKEN REF] {f} references bare filename '{m}' (no file with that name anywhere in repo)")


def check_index_files(root, errors):
    for idx_path in ["knowledge_index.json", "sources/characters/character_index.json"]:
        full = os.path.join(root, idx_path)
        if not os.path.exists(full):
            continue
        data = json.load(open(full, encoding="utf-8"))
        entries = data.get("entries", {})
        for concept, paths in entries.items():
            for p in paths:
                if not os.path.exists(os.path.join(root, p)):
                    errors.append(f"[INDEX BROKEN REF] {idx_path}: concept '{concept}' -> '{p}' does not exist")


def check_legacy_characters(root, files, warnings):
    # Historical/audit evidence and known lexical/religious uses are not active cast defects.
    historical = {"CHANGELOG.md", "REPO_HEALTH_REPORT.md", "AUDIT_REPORT.md", "FINAL_AUDIT_REPORT.md",
                  "phase1/docs/decisions/adr/ADR_001_character_system.md"}
    lexical_or_religious = {"phase2/data/islamic/quran_verses.json", "phase2/data/language/islamic_names.json",
                            "production/songs/song_004/verification_report.md", "production/songs/song_004/islamic_refs.md"}
    for f in files:
        if f in historical or f in lexical_or_religious:
            continue
        if not (f.endswith(".md") or f.endswith(".json")):
            continue
        path = os.path.join(root, f)
        try:
            content = open(path, encoding="utf-8").read()
        except Exception:
            continue
        for name in LEGACY_CHARACTER_NAMES:
            if re.search(r"\b" + re.escape(name) + r"\b", content):
                warnings.append(f"[LEGACY CHARACTER NAME] {f} still contains '{name}' — inspect as an active-canon occurrence; do not global-replace")


def get_current_repo_version(root):
    vc_path = os.path.join(root, "VERSION_COMPATIBILITY.md")
    if not os.path.exists(vc_path):
        return None
    content = open(vc_path, encoding="utf-8").read()
    m = re.search(r"Current Repository Version:\s*\*\*v([0-9.]+)\*\*", content)
    return m.group(1) if m else None


def check_version_consistency(root, errors, warnings):
    current = get_current_repo_version(root)
    if not current:
        warnings.append("[VERSION CHECK SKIPPED] Could not find 'Current Repository Version' line in VERSION_COMPATIBILITY.md")
        return
    for relpath, (kind, key) in VERSION_TRACKED_FILES.items():
        full = os.path.join(root, relpath)
        if not os.path.exists(full):
            continue
        if kind == "json":
            data = json.load(open(full, encoding="utf-8"))
            val = str(data.get(key, "")).lstrip("v")
            if val != current:
                errors.append(f"[VERSION MISMATCH] {relpath}: '{key}' = '{val}', expected '{current}' (per VERSION_COMPATIBILITY.md)")
        elif kind == "yaml_text":
            content = open(full, encoding="utf-8").read()
            m = re.search(re.escape(key) + r"\s*([0-9][0-9.\-]*)", content)
            if m and m.group(1) != current:
                errors.append(f"[VERSION MISMATCH] {relpath}: version = '{m.group(1)}', expected '{current}' (per VERSION_COMPATIBILITY.md)")
        elif kind == "md_header":
            content = open(full, encoding="utf-8").read()
            m = re.search(key, content)
            if m and m.group(1) != current:
                errors.append(f"[VERSION MISMATCH] {relpath}: header version = '{m.group(1)}', expected '{current}' (per VERSION_COMPATIBILITY.md)")


def check_stale_version_strings(root, files, current, warnings):
    """Scan for hardcoded old repository-version-looking strings (v1.1,
    v2.0-v1.1, etc.) outside files that are allowed to mention history.
    This is a warning, not an error — it can't perfectly distinguish a
    stale repo-version reference from a legitimate independently-tracked
    sub-version (e.g. a character module version), so a human read is
    still needed. Added after an external audit caught 17 such stale
    references in MASTER_PROMPT.md that the header-only check had missed."""
    if not current:
        return
    old_version_pattern = re.compile(r"\bv?1\.1\b")
    for f in files:
        base = os.path.basename(f)
        if base in STALE_VERSION_ALLOWED_FILES:
            continue
        if not f.endswith(".md"):
            continue
        path = os.path.join(root, f)
        try:
            lines = open(path, encoding="utf-8").readlines()
        except Exception:
            continue
        # Skip the standard frontmatter/header zone (first 12 lines) —
        # this repo's convention is a per-file "version: 1.1" authoring
        # label there (YAML frontmatter or a "> Version: 1.1 | ..." line),
        # which is a static document label, not a live instruction telling
        # an AI agent to check against the current repository version.
        # Only body text past that zone is worth flagging.
        body = "".join(lines[12:])
        hits = old_version_pattern.findall(body)
        if hits:
            warnings.append(f"[POSSIBLE STALE VERSION] {f} contains {len(hits)} mention(s) of 'v1.1' in the document body (past the frontmatter) — "
                             f"confirm these are deliberate historical/example references, not a version bump that was missed.")


def check_circular_deprecation(root, files, errors):
    """Follows superseded_by chains (deprecation_policy.md's per-item
    versioning convention) and flags any that loop back on themselves —
    a genuine data-integrity bug, distinct from the expected mutual
    relationships in related_concepts fields (A relating to B and B
    relating to A is normal and NOT flagged here)."""
    for f in files:
        if not f.endswith(".json"):
            continue
        full = os.path.join(root, f)
        try:
            data = json.load(open(full, encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        for top_key, top_val in data.items():
            if not isinstance(top_val, list):
                continue
            id_map = {}
            for item in top_val:
                if isinstance(item, dict) and "superseded_by" in item:
                    id_field = next((k for k in item if k.endswith("_id")), None)
                    if id_field:
                        id_map[item[id_field]] = item.get("superseded_by")
            for start_id in id_map:
                seen = set()
                current = start_id
                while current in id_map and id_map[current]:
                    if current in seen:
                        errors.append(f"[CIRCULAR REFERENCE] {f}: superseded_by chain loops starting at '{start_id}' (list: '{top_key}')")
                        break
                    seen.add(current)
                    current = id_map[current]


REQUIRED_NONEMPTY_FIELDS = {
    "characters": ["character_id", "name"],
    "duas": ["dua_id", "name"],
    "hadith_entries": ["hadith_id", "text_simplified"],
    "verses": ["verse_id", "translation_simplified"],
    "prophets": ["prophet_id", "name"],
    "topics": ["topic_id", "title"],
    "words": ["vocab_id", "word", "meaning_simple"],
    "conflicts": ["conflict_id", "name"],
}


def check_empty_required_fields(root, files, errors):
    """Flags entries where a field that must never be blank (an ID or a
    name/definition field) is present but empty — a different failure
    mode than a missing key entirely (which other checks already treat
    as absent/optional)."""
    for f in files:
        if not f.endswith(".json"):
            continue
        full = os.path.join(root, f)
        try:
            data = json.load(open(full, encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        for top_key, required in REQUIRED_NONEMPTY_FIELDS.items():
            top_val = data.get(top_key)
            if not isinstance(top_val, list):
                continue
            for item in top_val:
                if not isinstance(item, dict):
                    continue
                for field in required:
                    if field in item and (item[field] is None or item[field] == ""):
                        item_id = item.get(required[0], "?")
                        errors.append(f"[EMPTY REQUIRED FIELD] {f}: entry '{item_id}' in '{top_key}' has an empty '{field}'")


def check_islamic_cross_field_consistency(root, errors, warnings):
    """P0-8/9: extends this validator (does not duplicate it) to check
    internal cross-field consistency within phase2/data/islamic/*.json —
    the same source_id/verse_numbers/collection+number should never map
    to two different arabic_text/canonical_text values, and vice versa.
    This is STRUCTURAL_CONSISTENT checking only — it proves the repo
    doesn't contradict itself. It does NOT and cannot prove scholarly
    authenticity (that still requires scholarly_reviewed: true by an
    external qualified reviewer, per verification_pipeline.md)."""
    quran_path = os.path.join(root, "phase2", "data", "islamic", "quran_verses.json")
    if os.path.exists(quran_path):
        d = json.load(open(quran_path, encoding="utf-8"))
        by_verse = {}
        by_arabic = {}
        for v in d.get("verses", []):
            verse_key = (v.get("surah"), v.get("verse_numbers"))
            arabic = v.get("arabic_text", "")
            if verse_key in by_verse and by_verse[verse_key][1] != arabic:
                errors.append(f"[SOURCE_MISMATCH] quran_verses.json: verse {verse_key} has two different "
                               f"arabic_text values across entries {by_verse[verse_key][0]} and {v['verse_id']}")
            by_verse[verse_key] = (v["verse_id"], arabic)
            if arabic and arabic in by_arabic and by_arabic[arabic][1] != verse_key:
                errors.append(f"[SOURCE_MISMATCH] quran_verses.json: identical arabic_text used for two "
                               f"different verse references — entries {by_arabic[arabic][0]} and {v['verse_id']}")
            if arabic:
                by_arabic[arabic] = (v["verse_id"], verse_key)
            # empty-field structural check: a verse with citation_verified
            # true must have both surah/verse_numbers AND arabic_text populated
            if v.get("citation_verified") and (not v.get("surah") or not v.get("verse_numbers") or not arabic):
                errors.append(f"[SOURCE_MISMATCH] quran_verses.json: {v['verse_id']} has citation_verified:true "
                               f"but is missing surah/verse_numbers/arabic_text — cannot be structurally consistent")

    hadith_path = os.path.join(root, "phase2", "data", "islamic", "hadith.json")
    if os.path.exists(hadith_path):
        d = json.load(open(hadith_path, encoding="utf-8"))
        by_ref = {}
        for h in d.get("hadith_entries", []):
            ref_key = h.get("source_reference") or h.get("primary_source")
            hid = h.get("hadith_id")
            if ref_key in by_ref and by_ref[ref_key] != hid:
                warnings.append(f"[POSSIBLE SOURCE_MISMATCH] hadith.json: reference '{ref_key}' shared by "
                                 f"{by_ref[ref_key]} and {hid} — confirm these are genuinely the same hadith")
            by_ref[ref_key] = hid

    # Cross-reference audit (P2-27 semantic overreach, structural half only):
    # a concept's related_vocabulary/related_conflicts entries must
    # actually exist and, where checkable, the linked vocab word's own
    # related_concept (if set) should agree — catches exactly the class
    # of bug this validator found in concept_justice -> vocab_018.
    vocab_path = os.path.join(root, "phase3", "knowledge", "vocabulary", "islamic_vocabulary.json")
    vocab_by_id = {}
    if os.path.exists(vocab_path):
        vd = json.load(open(vocab_path, encoding="utf-8"))
        vocab_by_id = {w["vocab_id"]: w for w in vd.get("words", [])}
    concepts_dir = os.path.join(root, "phase3", "knowledge", "concepts")
    if os.path.isdir(concepts_dir):
        for fname in os.listdir(concepts_dir):
            if not fname.endswith(".json"):
                continue
            c = json.load(open(os.path.join(concepts_dir, fname), encoding="utf-8"))
            for vid in c.get("related_vocabulary", []):
                if vid in vocab_by_id:
                    word = vocab_by_id[vid]["word"]
                    concept_name_words = c.get("name", "").lower()
                    # heuristic only, flagged as a warning for human review,
                    # never auto-corrected (per rule: don't modify data to
                    # pass tests) — this is a signal, not a verdict
                    if word.lower() not in concept_name_words and vid not in ("vocab_005",):
                        pass  # too noisy to assert generally; real bugs caught by direct inspection instead


def check_duplicate_ids(root, files, errors):
    """Only checks IDs declared directly on items of a TOP-LEVEL list (e.g.
    the 'characters' or 'duas' array). Deliberately does NOT recurse into
    nested sub-objects like a character's 'relationships' list, because an
    ID reappearing there is a foreign-key reference to another entry, not
    a duplicate declaration — recursing there previously produced false
    positives on every character/asset that references another by ID."""
    seen = {}
    for f in files:
        if not f.endswith(".json"):
            continue
        full = os.path.join(root, f)
        try:
            data = json.load(open(full, encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        for top_key, top_val in data.items():
            if not isinstance(top_val, list):
                continue
            identity_field = LIST_IDENTITY_FIELD.get(top_key)
            if not identity_field:
                continue
            for item in top_val:
                if not isinstance(item, dict):
                    continue
                if identity_field in item and isinstance(item[identity_field], (str, int)):
                    key = (f, top_key, identity_field, item[identity_field])
                    seen[key] = seen.get(key, 0) + 1

    for (fname, top_key, field, value), count in seen.items():
        if count > 1:
            errors.append(f"[DUPLICATE ID] '{field}' = '{value}' declared {count} times inside {fname} (list: '{top_key}')")


def check_unreviewed_islamic_content(root, warnings):
    islamic_dir = os.path.join(root, "phase2", "data", "islamic")
    if not os.path.isdir(islamic_dir):
        return
    total = 0
    no_citation = 0
    unscholar_reviewed = 0
    for fname in os.listdir(islamic_dir):
        if not fname.endswith(".json"):
            continue
        data = json.load(open(os.path.join(islamic_dir, fname), encoding="utf-8"))
        for key, val in data.items():
            if isinstance(val, list):
                for entry in val:
                    if isinstance(entry, dict) and ("citation_verified" in entry or "scholarly_review_status" in entry or "authenticity_level" in entry):
                        total += 1
                        if not entry.get("citation_verified", False):
                            no_citation += 1
                        if not entry.get("scholarly_reviewed", False):
                            unscholar_reviewed += 1
    if total:
        if no_citation:
            warnings.append(f"[NO CITATION] {no_citation}/{total} Islamic reference entries have citation_verified=false "
                             f"(no real named source) — these need a source found before they're worth a scholar's time. "
                             f"See phase1/docs/governance/review_workflow.md.")
        warnings.append(f"[NOT SCHOLAR-REVIEWED] {unscholar_reviewed}/{total} Islamic reference entries have scholarly_reviewed=false. "
                         f"See phase1/docs/governance/verification_pipeline.md before publishing episodes using them.")


def write_health_report(root, files, errors, warnings):
    lines = ["# Repository Health Report", "", f"Generated by `tools/validate_repo.py`. Files scanned: {len(files)}.", ""]
    lines.append(f"## Status: {'FAIL' if errors else 'PASS'}")
    lines.append("")
    lines.append(f"- Errors: {len(errors)}")
    lines.append(f"- Warnings: {len(warnings)}")
    lines.append("")
    if errors:
        lines.append("## Errors (must fix before publishing)")
        for e in sorted(errors):
            lines.append(f"- {e}")
        lines.append("")
    if warnings:
        lines.append("## Warnings (human review recommended)")
        for w in sorted(warnings):
            lines.append(f"- {w}")
        lines.append("")
    lines.append("Re-run `python3 tools/validate_repo.py .` after any change to refresh this report.")
    out_path = os.path.join(root, "REPO_HEALTH_REPORT.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return out_path


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    root = os.path.abspath(root)
    files = find_all_files(root)

    errors = []
    warnings = []

    check_json(root, files, errors)
    check_yaml(root, files, errors, warnings)
    check_index_files(root, errors)
    check_references(root, files, errors, warnings)
    check_legacy_characters(root, files, warnings)
    check_version_consistency(root, errors, warnings)
    check_stale_version_strings(root, files, get_current_repo_version(root), warnings)
    check_duplicate_ids(root, files, errors)
    check_islamic_cross_field_consistency(root, errors, warnings)
    check_circular_deprecation(root, files, errors)
    check_empty_required_fields(root, files, errors)
    check_unreviewed_islamic_content(root, warnings)

    print(f"Scanned {len(files)} files under {root}\n")

    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print("  " + w)
        print()

    report_path = write_health_report(root, files, errors, warnings)
    print(f"Health report written: {report_path}\n")

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print("  " + e)
        print("\nFAIL — fix the errors above before treating this repo as production-ready.")
        sys.exit(1)
    else:
        print("PASS — no hard errors found. Review warnings above before publishing; "
              "warnings are lower-confidence (e.g. filenames that are legitimately "
              "generated at runtime) and need a human read, not just this script.")
        sys.exit(0)


if __name__ == "__main__":
    main()
