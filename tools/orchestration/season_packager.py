"""
tools/orchestration/season_packager.py

The season-level packaging identified as missing in the Phase 5 gap
analysis (package_episode.py only knows about single legacy episodes;
package_release.py zips the whole source repo, not a season's output).

Reuses tools/release_hygiene.py's is_prohibited() UNCHANGED for
exclusion -- the same function that already correctly excludes .git,
caches, .env, bytecode, etc. Not re-implementing that logic here.

REAL BUG FOUND AND FIXED HERE (confirmed by direct execution, not
assumed): registry files (character_bible, environment_bible,
prop_registry, camera_bible) were listed in ARTIFACT_ROOTS but NEVER
actually got packaged. The per-file inclusion filter checked whether
season_id or an episode_id appeared as a substring of the file's path
-- correct for season-scoped artifacts (clip_state/<episode_id>/...,
duration_gate/<episode_id>.json), a category error for registries,
whose filenames (char_001_zayd.json, camera_bible.json) are global and
never contain a season/episode identifier. Confirmed with a direct
test: packaging a season with real character_bible files present
produced a zip containing zero of them, despite the directory being
listed.

Fixed by splitting artifact roots into two real categories instead of
patching the filter: SEASON_SCOPED_ROOTS (season-id/episode-id
filtering is correct here, unchanged) and REGISTRY_ROOTS (included by
actually reading the season's authored episodes and collecting which
character/environment/prop IDs they reference -- precise, and
correctly picks up a brand-new registry entry a season itself created,
without bundling the entire global registry from every other season).
"""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from release_hygiene import is_prohibited  # noqa: E402

# Season/episode-scoped: filenames genuinely contain the season_id or an
# episode_id, so the existing substring filter is correct for these.
SEASON_SCOPED_ROOTS = [
    "continuity/season_concepts", "continuity/authored_episodes", "continuity/story_state",
    "continuity/clip_plan", "continuity/clip_state", "continuity/generated_requests",
    "continuity/qa_reports", "continuity/generated_videos", "continuity/frames",
    "continuity/assembled_episodes", "continuity/assembly_reports", "continuity/job_state",
    "continuity/duration_gate", "continuity/islamic_gate", "continuity/song_gate",
    "continuity/continuity_gate", "continuity/season_acceptance",
]

# Global registries: NOT season-scoped by design (a character like Zayd is
# shared across every season), so filename substring matching can never
# work here -- inclusion is reference-driven instead, see
# collect_referenced_registry_ids().
REGISTRY_ROOTS = {
    "character": "continuity/character_bible",
    "environment": "continuity/environment_bible",
    "prop": "continuity/prop_registry",
}
CAMERA_BIBLE_PATH = "continuity/camera_bible/camera_bible.json"  # single shared file, not per-entity


def collect_referenced_registry_ids(root: Path, episode_ids: list[str]) -> dict:
    """Reads each authored episode's actual scenes and returns exactly
    the character/environment/prop IDs the season references -- this is
    what makes registry packaging correct for a newly-created entry
    (e.g. a season's own new environment/prop) without bundling
    unrelated seasons' entire character rosters."""
    referenced = {"character": set(), "environment": set(), "prop": set()}
    for episode_id in episode_ids:
        path = root / "continuity" / "authored_episodes" / f"{episode_id}.json"
        if not path.exists():
            continue
        episode = json.loads(path.read_text(encoding="utf-8"))
        for scene in episode.get("scenes", []):
            referenced["character"].update(scene.get("characters_present", []))
            if scene.get("location_id"):
                referenced["environment"].add(scene["location_id"])
            referenced["prop"].update(scene.get("props_visible", []))
    return referenced


def build_production_status_report(root: Path, season_id: str, job: dict) -> dict:
    total_clips = sum(len(e["clips"]) for e in job["episodes"].values())
    status_counts: dict = {}
    for e in job["episodes"].values():
        for c in e["clips"].values():
            status_counts[c["status"]] = status_counts.get(c["status"], 0) + 1

    # Real gap found and fixed: this report never included the actual
    # Season Acceptance result, even though the Master Prompt requires
    # the final status to report it plainly, note included.
    acceptance_path = root / "continuity" / "season_acceptance" / f"{season_id}.json"
    season_acceptance = None
    if acceptance_path.exists():
        acc = json.loads(acceptance_path.read_text(encoding="utf-8"))
        season_acceptance = {"status": acc.get("status"), "note": acc.get("note")}

    return {
        "season_id": season_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "season_status": job["status"],
        "episode_count": job["episode_count"],
        "episodes": {
            eid: {"status": e["status"], "clip_count": len(e["clips"])}
            for eid, e in job["episodes"].items()
        },
        "total_clips": total_clips,
        "clip_status_breakdown": status_counts,
        "season_acceptance": season_acceptance,
    }


def package_season(root, season_id, job, output_path=None):
    root = Path(root)
    report = build_production_status_report(root, season_id, job)
    report_path = root / "continuity" / "production_status" / f"{season_id}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    included_files = []

    for artifact_root in SEASON_SCOPED_ROOTS:
        d = root / artifact_root
        if not d.exists():
            continue
        for p in sorted(d.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(root)
            if is_prohibited(rel):
                continue
            if season_id not in str(p) and not any(eid in str(p) for eid in job["episodes"]):
                continue
            included_files.append(rel)

    referenced = collect_referenced_registry_ids(root, list(job["episodes"].keys()))
    for kind, ids in referenced.items():
        reg_root = root / REGISTRY_ROOTS[kind]
        for entity_id in sorted(ids):
            p = reg_root / f"{entity_id}.json"
            if p.exists():
                rel = p.relative_to(root)
                if not is_prohibited(rel):
                    included_files.append(rel)
    camera_bible_full = root / CAMERA_BIBLE_PATH
    if camera_bible_full.exists() and job["episodes"]:
        included_files.append(camera_bible_full.relative_to(root))

    included_files.append(report_path.relative_to(root))

    manifest_path = root / "continuity" / "manifests" / f"{season_id}.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    # Include the manifest's own path in the count BEFORE writing it, so
    # the manifest accurately describes the zip it ends up inside.
    included_files.append(manifest_path.relative_to(root))
    manifest = {
        "season_id": season_id, "file_count": len(set(included_files)),
        "files": sorted(str(f) for f in set(included_files)),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    out_path = Path(output_path) if output_path else root / f"{season_id}_season_package.zip"
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel in sorted(set(included_files)):
            full = root / rel
            info = zipfile.ZipInfo(rel.as_posix(), (2026, 8, 6, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, full.read_bytes(), compresslevel=9)

    sha256 = hashlib.sha256(out_path.read_bytes()).hexdigest()
    return {"zip_path": str(out_path), "sha256": sha256, "manifest": manifest, "status_report": report}


def verify_frozen_package(zip_path) -> dict:
    """Independent, from-scratch re-verification of an already-built
    ZIP -- never trusts manifest.json on its own claims. Reopens the
    real zip, recomputes its real membership and hash, and reports
    whatever the manifest.json entry INSIDE that same zip claims,
    side by side, so any drift between the two is visible rather than
    silently accepted."""
    zip_path = Path(zip_path)
    sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    with zipfile.ZipFile(zip_path) as z:
        integrity_error = z.testzip()
        real_names = set(z.namelist())
        manifest_entries = [n for n in real_names if n.startswith("continuity/manifests/")]
        manifest_claim = None
        if manifest_entries:
            manifest_claim = json.loads(z.read(manifest_entries[0]).decode("utf-8"))

    result = {
        "sha256": sha256,
        "real_file_count": len(real_names),
        "integrity_ok": integrity_error is None,
        "manifest_present": manifest_claim is not None,
    }
    if manifest_claim is not None:
        result["manifest_claimed_count"] = manifest_claim.get("file_count")
        result["count_matches"] = manifest_claim.get("file_count") == len(real_names)
        claimed_files = set(manifest_claim.get("files", []))
        result["file_list_matches"] = claimed_files == real_names
        result["files_in_zip_not_in_manifest"] = sorted(real_names - claimed_files)
        result["files_in_manifest_not_in_zip"] = sorted(claimed_files - real_names)
    return result
