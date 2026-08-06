#!/usr/bin/env python3
"""
tools/continuity/migrate_v272_to_continuity.py

Derives the new continuity/ bibles (character, environment, prop) from
the existing v2.72 source-of-truth files. Non-destructive: never edits
anything under sources/. Idempotent: safe to re-run, always regenerates
continuity/ fresh from source rather than patching in place, so it can
never drift out of sync with the data it was derived from.

Where the old data genuinely doesn't have a field the new schema wants
(e.g. an explicit lighting default), the migration writes
"needs_review": true against that field rather than inventing a value.
See MIGRATION_REPORT.md (written alongside the output) for the full
list of what needs a human pass before Phase 3 consumes it.

Usage:
    python3 tools/continuity/migrate_v272_to_continuity.py [repo_root]
    python3 tools/continuity/migrate_v272_to_continuity.py --dry-run [repo_root]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DEFAULT = Path(__file__).resolve().parents[2]


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict, dry_run: bool):
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Character Bible
# ---------------------------------------------------------------------------

def migrate_characters(root: Path, dry_run: bool) -> tuple[list[dict], list[str]]:
    src = root / "sources" / "characters" / "character_master_library.json"
    report: list[str] = []
    if not src.exists():
        report.append(f"SKIPPED characters: {src} not found")
        return [], report

    data = _read_json(src)
    written = []
    for c in data.get("characters", []):
        cid = c["character_id"]
        ref_image = c.get("approved_reference_image")
        ref_status = c.get("approved_reference_image_status", "")
        image_path = root / ref_image if ref_image else None
        image_resolves = bool(image_path and image_path.exists())

        if ref_image and not image_resolves:
            report.append(
                f"CHARACTER {cid}: reference image path '{ref_image}' does not "
                f"resolve on disk -- excluded from reference_images list"
            )
        if not ref_image:
            report.append(f"CHARACTER {cid}: no approved_reference_image at all -- needs_review")

        bible = {
            "schema_version": "1.0",
            "character_id": cid,
            "canonical_name": c.get("canonical_name"),
            "aliases": c.get("aliases", []),
            "role_relation": c.get("role_relation"),
            "age": c.get("age"),
            "is_speaking": c.get("is_speaking"),
            "appearance": {
                "canonical_description": c.get("canonical_image_prompt"),
                "needs_review": c.get("canonical_image_prompt") is None,
            },
            "turnaround_prompt": c.get("turnaround_prompt"),
            "expression_prompt": c.get("expression_prompt"),
            "colours": {
                "needs_review": True,
                "note": (
                    "v2.72 source data describes colours in prose inside "
                    "canonical_image_prompt/turnaround_prompt rather than as "
                    "structured hex values. Not fabricating hex codes here -- "
                    "the prose description remains authoritative until a human "
                    "extracts structured colour values, if that's ever needed "
                    "for a non-text-prompt use case."
                ),
            },
            "voice": {
                "voice_profile_text": c.get("voice_profile_text"),
                "voice_master": c.get("voice_master"),
            },
            "restrictions": c.get("restrictions"),
            "production_priority": c.get("production_priority"),
            "approval_status": c.get("approval_status"),
            "asset_status": c.get("asset_status"),
            "reference_images": (
                [{
                    "asset_id": f"{cid}_approved_reference",
                    "path": ref_image,
                    "role": "asset",
                    "status": ref_status,
                    "resolves_on_disk": image_resolves,
                }]
                if ref_image else []
            ),
            "relationships": [],  # not present in v2.72 source in structured form; needs_review below
            "relationships_needs_review": True,
            "source_of_truth": False,
            "provenance": "migrated_from:sources/characters/character_master_library.json",
            "provenance_note": (
                "This file is DERIVED. sources/characters/character_master_library.json "
                "remains the authored source of truth; re-run this migration if that "
                "file changes rather than hand-editing this output."
            ),
        }
        out_path = root / "continuity" / "character_bible" / f"{cid}.json"
        _write_json(out_path, bible, dry_run)
        written.append(cid)

    report.insert(0, f"Characters migrated: {len(written)} of {len(data.get('characters', []))}")
    return written, report


# ---------------------------------------------------------------------------
# Environment Bible
# ---------------------------------------------------------------------------

def migrate_environments(root: Path, dry_run: bool) -> tuple[list[str], list[str]]:
    src = root / "sources" / "production" / "location_library.json"
    report: list[str] = []
    if not src.exists():
        report.append(f"SKIPPED environments: {src} not found")
        return [], report

    data = _read_json(src)
    written = []
    for loc in data.get("locations", []):
        lid = loc["location_id"]
        lighting_established = "not yet established" not in json.dumps(
            loc.get("time_variants", {})
        )
        bible = {
            "schema_version": "1.0",
            "location_id": lid,
            "display_name": loc.get("name"),
            "canonical_description": loc.get("canonical_description"),
            "layout": loc.get("layout"),
            "architecture": loc.get("architecture"),
            "materials": loc.get("materials"),
            "colour_palette": loc.get("color_palette"),
            "furniture": loc.get("furniture", []),
            "important_objects": loc.get("important_objects", []),
            "lighting_default": {
                "baseline": loc.get("lighting_baseline"),
                "time_variants": loc.get("time_variants", {}),
                "needs_review": not lighting_established,
            },
            "weather_default": {
                "value": None,
                "needs_review": True,
                "note": "Not tracked in v2.72 source data (interior location); flagged for episodes involving weather/exterior continuity.",
            },
            "reference_images": (
                [{"path": loc["reference_assets"]}] if loc.get("reference_assets") else []
            ),
            "continuity_notes": loc.get("gemini_compact_location_lock"),
            "approval_status": loc.get("approval_status"),
            "source_of_truth": False,
            "provenance": "migrated_from:sources/production/location_library.json",
        }
        out_path = root / "continuity" / "environment_bible" / f"{lid}.json"
        _write_json(out_path, bible, dry_run)
        written.append(lid)
        if not loc.get("reference_assets"):
            report.append(f"ENVIRONMENT {lid}: no reference image on file -- text-lock only until one exists")

    report.insert(0, f"Environments migrated: {len(written)} of {len(data.get('locations', []))}")
    return written, report


# ---------------------------------------------------------------------------
# Prop Registry
# ---------------------------------------------------------------------------

def migrate_props(root: Path, dry_run: bool) -> tuple[list[str], list[str]]:
    src = root / "sources" / "production" / "prop_registry.json"
    report: list[str] = []
    if not src.exists():
        report.append(f"SKIPPED props: {src} not found")
        return [], report

    data = _read_json(src)
    written = []
    for prop in data.get("props", []):
        pid = prop["prop_id"]
        bible = {
            "schema_version": "1.0",
            "prop_id": pid,
            "display_name": prop.get("name"),
            "appearance": {
                "canonical_description": prop.get("canonical_appearance"),
                "colour": prop.get("color"),
                "size": prop.get("size"),
                "material": prop.get("material"),
            },
            "ownership": {"belongs_to_character_id": prop.get("owner")},
            "default_position": {"needs_review": True, "note": "Not tracked in v2.72 source; set per-scene until a canonical default is authored."},
            "continuity_rules": [
                "Must not disappear between clips in the same scene/continuity thread unless the story explicitly removes it.",
                "Must not duplicate (two instances in frame) unless the story explicitly requires it.",
            ],
            "reference_images": (
                [{"path": prop["reference_asset"]}] if prop.get("reference_asset") else []
            ),
            "source_of_truth": False,
            "provenance": "migrated_from:sources/production/prop_registry.json",
        }
        out_path = root / "continuity" / "prop_registry" / f"{pid}.json"
        _write_json(out_path, bible, dry_run)
        written.append(pid)
        if not prop.get("reference_asset"):
            report.append(f"PROP {pid}: no reference image on file -- text-lock only until one exists")

    report.insert(0, f"Props migrated: {len(written)} of {len(data.get('props', []))}")
    return written, report


# ---------------------------------------------------------------------------
# Report + entrypoint
# ---------------------------------------------------------------------------

def write_report(root: Path, sections: dict[str, list[str]], dry_run: bool):
    lines = [
        "# Continuity Migration Report",
        "",
        f"Dry run: {dry_run}",
        "",
        "Non-destructive migration from v2.72 sources/ into continuity/ bibles.",
        "Nothing under sources/ was modified. Re-running this script regenerates",
        "continuity/ output fresh; it never patches in place.",
        "",
    ]
    for title, entries in sections.items():
        lines.append(f"## {title}")
        lines.append("")
        if not entries:
            lines.append("(nothing to report)")
        for e in entries:
            lines.append(f"- {e}")
        lines.append("")

    review_items = [
        e for entries in sections.values() for e in entries
        if "needs_review" in e.lower() or "no reference image" in e.lower()
        or "does not resolve" in e.lower()
    ]
    lines.append("## Human review checklist before Phase 3 consumes these bibles")
    lines.append("")
    if review_items:
        for e in review_items:
            lines.append(f"- [ ] {e}")
    else:
        lines.append("(none flagged)")
    lines.append("")

    text = "\n".join(lines)
    if not dry_run:
        (root / "continuity" / "MIGRATION_REPORT.md").write_text(text, encoding="utf-8")
    return text


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root", nargs="?", default=str(ROOT_DEFAULT))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()

    chars, char_report = migrate_characters(root, args.dry_run)
    envs, env_report = migrate_environments(root, args.dry_run)
    props, prop_report = migrate_props(root, args.dry_run)

    report_text = write_report(root, {
        "Characters": char_report,
        "Environments": env_report,
        "Props": prop_report,
    }, args.dry_run)

    print(report_text)
    print(f"\nTOTAL: {len(chars)} characters, {len(envs)} environments, {len(props)} props"
          f" {'(dry run, nothing written)' if args.dry_run else 'written to continuity/'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
