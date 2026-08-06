#!/usr/bin/env python3
"""
package_episode.py — scaffolds output_package/ and zips it.

This is what turns MASTER_PROMPT.md Step 20 ("Produce Final Output") from a
description into something an agent can actually execute. Your coding agent
should, after generating the 25 output sections described in MASTER_PROMPT.md,
write each one into output_package/<episode_slug>/ using the exact filenames
below, then run this script to zip it into a single downloadable file.

Usage:
    python3 tools/package_episode.py <episode_slug>

Example:
    python3 tools/package_episode.py ep_004_eating_dua

This will:
  1. Confirm output_package/<episode_slug>/ exists.
  2. Confirm every required output file listed below is present (warns, does
     not block, on missing optional files like thumbnail A/B variants).
  3. Zip the folder into output_package/<episode_slug>.zip.
"""
import json
import os
import re
import subprocess
import sys
import zipfile

REQUIRED_FILES = [
    "episode_summary.md",
    "learning_goals.md",
    "curriculum_map.md",
    "islamic_refs.md",
    "vocabulary.md",
    "story_outline.md",
    "complete_script.md",
    "narration.md",
    "dialogue.md",
    "scene_breakdown.md",
    "camera_directions.md",
    "animation_directions.md",
    "image_prompts.md",
    "thumbnail.md",
    "music_notes.md",
    "lyrics_and_song.md",
    "sound_effects.md",
    "voice_instructions.md",
    "subtitles.srt",
    "youtube_title.md",
    "description.md",
    "seo_metadata.md",
    "tags.md",
    "hashtags.md",
    "thumbnail_text.md",
    "qa_checklist.md",
    "validation_report.md",
    "editing_notes.md",
    "verification_report.md",
]


def check_review_status(slug):
    """Warn (don't block) if the episode isn't 'approved' in review_queue.json.
    Non-blocking because a creator may legitimately want to package a
    generated/reviewed episode for their own preview before formal
    approval — but the warning must be impossible to miss."""
    queue_path = os.path.join("phase2", "data", "database", "review_queue.json")
    if not os.path.exists(queue_path):
        return False, "review_queue.json missing"
    try:
        data = json.load(open(queue_path, encoding="utf-8"))
    except Exception as e:
        return False, f"review_queue.json unreadable: {e}"
    entry = next((e for e in data.get("episodes", []) if e.get("episode_id") == slug), None)
    if entry is None:
        print(f"NOTE: '{slug}' is not tracked in review_queue.json yet — add an entry "
              f"(status: 'generated') per verification_pipeline.md.\n")
        return False, "episode not tracked in review_queue.json"
    status = entry.get("status", "generated")
    if status != "approved":
        print(f"*** WARNING: '{slug}' has review status '{status}', not 'approved'. ***")
        print("This package is NOT cleared for publication per verification_pipeline.md. Remember: episode-level review does not require Islamic knowledge (see verification_report.md); scholarly accuracy still needs an external qualified reviewer.")
        print("Draft packaging remains available for preview; FINAL packaging is blocked until status is 'approved'.\n")
        return False, status
    return True, status


def run_consistency_gate(slug):
    """Real packaging gate, closing a gap found during v2.17 rollback
    testing: packaging previously never checked episode_consistency_check.py
    at all. A BLOCKED-mode folder (report-only) is exempt — there's
    nothing to consistency-check in a folder with no episode content."""
    pkg_dir = os.path.join("output_package", slug)
    present = set(os.listdir(pkg_dir)) if os.path.isdir(pkg_dir) else set()
    if present == {"missing_knowledge_report.md"}:
        return True, {}  # Blocked-mode report-only package, nothing to check
    result = subprocess.run(
        [sys.executable, os.path.join("tools", "episode_consistency_check.py"), "check-episode", pkg_dir, "."],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print("*** PACKAGING BLOCKED: episode_consistency_check.py reported FAIL. ***")
        print("Fix the errors above before packaging — this gate exists so a package "
              "with real character-lock, fabricated-source, or excluded-claim-propagation "
              "problems can never be zipped and mistaken for production-ready output.")
        return False, {}

    # v2.38: compute real readiness from the check output, don't just
    # look at returncode. A SAFETY REVIEW_REQUIRED warning must
    # mechanically force publication_ready=false, not just print a
    # message that's easy to miss (the exact gap found in v2.38's P0).
    review_required_items = [line.strip() for line in result.stdout.splitlines()
                              if "SAFETY:" in line and "REVIEW_REQUIRED" in line]
    semantic_unclassified = [line.strip() for line in result.stdout.splitlines()
                              if "SEMANTIC SUPPORT UNCLASSIFIED" in line]
    readiness = {
        "technical_ready": True,  # got here, so consistency check passed
        "content_safety_ready": "review_required" if review_required_items else True,
        "review_required_items": review_required_items,
        "semantic_unclassified": semantic_unclassified,
        "publication_ready": not review_required_items and not semantic_unclassified,
    }
    return True, readiness


def check_review_resolution(slug, review_required_items):
    """v2.38: an explicit resolution record is required to clear
    REVIEW_REQUIRED for FINAL packaging — never auto-cleared by
    re-running the validator, never inferred from unrelated approvals."""
    path = os.path.join("phase2", "data", "safety", "review_resolutions.json")
    if not os.path.exists(path):
        return False, "No review_resolutions.json exists yet."
    resolutions = json.load(open(path))["resolutions"]
    matching = [r for r in resolutions if r.get("episode_id") == slug and r.get("resolved_decision") in ("ALLOW", "ALLOW_WITH_CONTEXT")]
    if matching:
        return True, matching
    return False, f"No resolution record found for '{slug}' in review_resolutions.json."


def islamic_entries_by_id():
    out = {}
    root = os.path.join("phase2", "data", "islamic")
    for name in os.listdir(root):
        if not name.endswith(".json"):
            continue
        try:
            data = json.load(open(os.path.join(root, name), encoding="utf-8"))
        except Exception:
            continue
        for value in data.values() if isinstance(data, dict) else []:
            if not isinstance(value, list):
                continue
            for item in value:
                if not isinstance(item, dict):
                    continue
                for k,v in item.items():
                    if k.endswith("_id") and isinstance(v, str):
                        out[v] = item
    return out

def final_religious_gate(slug):
    """Fail closed for FINAL publication when cited Islamic evidence is not scholar-reviewed
    or when the consistency checker reports unclassified semantic support."""
    report = os.path.join("output_package", slug, "verification_report.md")
    if not os.path.exists(report):
        return False, ["verification_report.md missing"]
    try:
        text = open(report, encoding="utf-8").read()
    except (OSError, UnicodeError) as exc:
        return False, [f"verification_report.md unreadable: {exc}"]
    evidence_lines = re.findall(r"(?m)^Evidence:\s*(.*)$", text)
    if not evidence_lines:
        return False, ["verification_report.md contains no Evidence entry"]
    ids = []
    problems=[]
    for raw in evidence_lines:
        value = raw.strip()
        if not re.fullmatch(r"[A-Za-z0-9_]+", value):
            problems.append(f"malformed Evidence entry: {value!r}")
        else:
            ids.append(value)
    ids = sorted(set(ids))
    entries = islamic_entries_by_id()
    for sid in ids:
        item=entries.get(sid)
        if item is None:
            problems.append(f"evidence id {sid!r} does not resolve in phase2/data/islamic")
        elif item.get("citation_verified") is not True or item.get("source_verified") is not True:
            problems.append(f"{sid}: citation/source verification incomplete")
        elif item.get("scholarly_reviewed") is not True:
            problems.append(f"{sid}: scholarly_reviewed is not true")
    return not problems, problems

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/package_episode.py <episode_slug> [--final]")
        sys.exit(1)

    slug = sys.argv[1]
    final_mode = "--final" in sys.argv[2:]
    review_approved, review_status = check_review_status(slug)
    if final_mode and not review_approved:
        print(f"*** FINAL PUBLICATION PACKAGE BLOCKED: review status is {review_status!r}, not 'approved'. ***")
        sys.exit(1)
    src_dir = os.path.join("output_package", slug)

    if not os.path.isdir(src_dir):
        print(f"ERROR: {src_dir} does not exist. Generate the output files there first.")
        sys.exit(1)

    gate_ok, readiness = run_consistency_gate(slug)
    if not gate_ok:
        print("No zip was created. Character-lock, fabricated-source, or excluded-claim "
              "problems must be fixed before this episode can be packaged at all.")
        sys.exit(1)

    if final_mode and readiness.get("semantic_unclassified"):
        print("*** FINAL PUBLICATION PACKAGE BLOCKED: semantic support remains unclassified. ***")
        for item in readiness["semantic_unclassified"]:
            print("  " + item)
        sys.exit(1)

    if final_mode:
        religious_ok, religious_problems = final_religious_gate(slug)
        if not religious_ok:
            print("*** FINAL PUBLICATION PACKAGE BLOCKED: religious-source publication gate not satisfied. ***")
            for item in religious_problems:
                print("  " + item)
            sys.exit(1)

    if final_mode and readiness.get("review_required_items"):
        resolved, detail = check_review_resolution(slug, readiness["review_required_items"])
        if not resolved:
            print("*** FINAL PUBLICATION PACKAGE BLOCKED ***")
            print("content_safety_ready: review_required -- publication_ready: false")
            for item in readiness["review_required_items"]:
                print("  " + item)
            print(f"Resolution check: {detail}")
            print("A --final package cannot be created until an explicit resolution record "
                  "exists in phase2/data/safety/review_resolutions.json for this episode. "
                  "A draft/test package (without --final) remains available for internal review.")
            sys.exit(1)
        else:
            print(f"Review resolution found, FINAL packaging proceeding: {detail}")
            readiness["publication_ready"] = True
            readiness["review_resolution"] = detail

    present = set(os.listdir(src_dir))

    # Execution mode detection (execution_modes.md): a Blocked-mode run
    # only ever produces missing_knowledge_report.md — checking the full
    # 27-file Production list against it would be noise, not signal.
    if present == {"missing_knowledge_report.md"} or (
        "missing_knowledge_report.md" in present and "episode_summary.md" not in present
    ):
        print(f"NOTE: '{slug}' looks like a BLOCKED-mode run (only missing_knowledge_report.md "
              f"present, no episode files) — per execution_modes.md, this is expected, not an error.")
        zip_path = os.path.join("output_package", f"{slug}.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in os.listdir(src_dir):
                zf.write(os.path.join(src_dir, f), f)
        print(f"Packaged (Blocked-mode report only): {zip_path}")
        return

    is_assisted = "missing_knowledge_report.md" in present
    if is_assisted:
        if final_mode:
            print("*** FINAL PUBLICATION PACKAGE BLOCKED: ASSISTED-mode output cannot be publication-ready without explicit approved promotion. ***")
            sys.exit(1)
        print(f"NOTE: '{slug}' looks like an ASSISTED-mode run (missing_knowledge_report.md "
              f"present alongside episode files) — per execution_modes.md, production_ready "
              f"should be false in validation_report.md. Verify that's set correctly.\n")

    missing = [f for f in REQUIRED_FILES if f not in present]
    if missing:
        if final_mode:
            print("ERROR — FINAL package is missing expected output files:")
            for m in missing:
                print("  " + m)
            sys.exit(1)
        print("WARNING — missing expected output files:")
        for m in missing:
            print("  " + m)
        print("Packaging anyway. Review before uploading.\n")

    zip_path = os.path.join("output_package", f"{slug}.zip")
    readiness_full = {
        "technical_ready": readiness.get("technical_ready", True),
        "content_safety_ready": readiness.get("content_safety_ready", True),
        "publication_ready": bool(review_approved) and not is_assisted and readiness.get("publication_ready", not readiness.get("review_required_items")),
        "package_mode": "FINAL" if final_mode else "DRAFT",
        "blocking_reasons": readiness.get("review_required_items", []) + ([] if review_approved else [f"review_status:{review_status}"]) + (["assisted_mode"] if is_assisted else []),
        "review_resolution": readiness.get("review_resolution"),
        "note": "publication_ready reflects content_safety_ready only. religious_source_ready/character_asset_ready/voice_ready are separate dimensions computed elsewhere in this repository (verification_pipeline.md, character_master_library.json) and are NOT rolled into this single field to avoid a misleading collapsed PASS.",
    }
    with open(os.path.join(src_dir, "readiness.json"), "w") as rf:
        json.dump(readiness_full, rf, indent=2)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(src_dir):
            for f in files:
                full = os.path.join(root, f)
                arcname = os.path.relpath(full, src_dir)
                zf.write(full, arcname)

    print(f"Packaged ({'FINAL' if final_mode else 'DRAFT'}): {zip_path}")
    print(f"publication_ready: {readiness_full['publication_ready']}")


if __name__ == "__main__":
    main()
