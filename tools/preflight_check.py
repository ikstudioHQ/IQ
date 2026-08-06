#!/usr/bin/env python3
"""
preflight_check.py — Repository Identity + Presence Guard (P0-1, P1-15, P1-24)

Runs BEFORE any generation step. Distinguishes CORRECT REPOSITORY from
WRONG/OLD/PARTIAL/NO REPOSITORY. Presence of files alone is not enough —
this checks identity (version match across the manifest chain) and
completeness (required anchor files exist).

Usage:
    python3 tools/preflight_check.py [repo_root]

Exit code 0 only for REPOSITORY_VERIFIED. Any other status exits 1 —
per execution_modes.md, a non-zero exit here means the caller MUST NOT
proceed to generation. Total repository absence must never enter
Assisted Mode; this script is the mechanism that makes that concrete
rather than aspirational.
"""
import json
import os
import re
import sys

REQUIRED_ANCHORS = [
    "knowledge_index.json",
    "repository_manifest.json",
    "VERSION_COMPATIBILITY.md",
    "DESIGN_PRINCIPLES.md",
    "AUTHORITY_HIERARCHY.md",
]
REQUIRED_ANCHOR_DIRS = [
    "phase2/data/islamic",
    "sources/characters/characters",
    "phase1/docs/governance",
    "phase2/data/config",
]

# Fingerprint inputs: a lightweight deterministic identity signal built
# from critical manifest/version fields + a stable count of canonical
# source files. Not a cryptographic guarantee — a fast, good-enough
# signal to catch "this is a different or stale checkout" cases.
FINGERPRINT_SOURCES = [
    "repository_manifest.json",
    "knowledge_index.json",
]


def get_declared_version(root):
    vc_path = os.path.join(root, "VERSION_COMPATIBILITY.md")
    if not os.path.exists(vc_path):
        return None
    content = open(vc_path, encoding="utf-8").read()
    m = re.search(r"Current Repository Version:\s*\*\*v([0-9.]+)\*\*", content)
    return m.group(1) if m else None


def compute_fingerprint(root):
    parts = []
    for relpath in FINGERPRINT_SOURCES:
        full = os.path.join(root, relpath)
        if not os.path.exists(full):
            parts.append(f"{relpath}:MISSING")
            continue
        try:
            data = json.load(open(full, encoding="utf-8"))
            parts.append(f"{relpath}:{data.get('repository_version', data.get('version', '?'))}")
        except Exception:
            parts.append(f"{relpath}:UNREADABLE")
    # count of canonical islamic source files as a coarse completeness signal
    islamic_dir = os.path.join(root, "phase2", "data", "islamic")
    n_islamic = len([f for f in os.listdir(islamic_dir) if f.endswith(".json")]) if os.path.isdir(islamic_dir) else 0
    parts.append(f"islamic_file_count:{n_islamic}")
    char_dir = os.path.join(root, "sources", "characters", "characters")
    n_chars = len([f for f in os.listdir(char_dir) if f.endswith(".md")]) if os.path.isdir(char_dir) else 0
    parts.append(f"character_file_count:{n_chars}")
    return "|".join(parts)


def run(root, expected_version=None, profile="distribution"):
    """profile=distribution permits local-only MASTER_PROMPT.md to be absent.
    profile=local requires it and validates its declared repository version."""
    """Returns (status, details_dict). status is one of:
    REPOSITORY_VERIFIED, REPOSITORY_INCOMPLETE, REPOSITORY_VERSION_MISMATCH,
    REPOSITORY_IDENTITY_UNVERIFIED, REPOSITORY_CONTEXT_UNAVAILABLE."""
    if not os.path.isdir(root):
        return "REPOSITORY_CONTEXT_UNAVAILABLE", {"reason": f"root path does not exist: {root}"}

    missing_files = [f for f in REQUIRED_ANCHORS if not os.path.isfile(os.path.join(root, f))]
    if profile not in {"distribution", "local"}:
        return "REPOSITORY_IDENTITY_UNVERIFIED", {"reason": f"unknown preflight profile: {profile}"}
    master_path = os.path.join(root, "MASTER_PROMPT.md")
    if profile == "local" and not os.path.isfile(master_path):
        missing_files.append("MASTER_PROMPT.md")
    missing_dirs = [d for d in REQUIRED_ANCHOR_DIRS if not os.path.isdir(os.path.join(root, d))]

    if len(missing_files) == len(REQUIRED_ANCHORS) and len(missing_dirs) == len(REQUIRED_ANCHOR_DIRS):
        # nothing at all resolves — total absence, not partial
        return "REPOSITORY_CONTEXT_UNAVAILABLE", {
            "reason": "None of the required repository anchors exist at this path.",
            "checked_root": os.path.abspath(root),
        }

    if missing_files or missing_dirs:
        return "REPOSITORY_INCOMPLETE", {
            "missing_files": missing_files,
            "missing_dirs": missing_dirs,
        }

    declared_version = get_declared_version(root)
    if declared_version is None:
        return "REPOSITORY_IDENTITY_UNVERIFIED", {"reason": "VERSION_COMPATIBILITY.md present but version line unparseable."}

    try:
        manifest = json.load(open(os.path.join(root, "repository_manifest.json"), encoding="utf-8"))
        index = json.load(open(os.path.join(root, "knowledge_index.json"), encoding="utf-8"))
    except Exception as e:
        return "REPOSITORY_IDENTITY_UNVERIFIED", {"reason": f"manifest/index unreadable: {e}"}

    manifest_version = str(manifest.get("repository_version", "")).lstrip("v")
    index_version = str(index.get("version", "")).lstrip("v")

    if manifest_version != declared_version or index_version != declared_version:
        return "REPOSITORY_VERSION_MISMATCH", {
            "declared_in_VERSION_COMPATIBILITY": declared_version,
            "repository_manifest_json": manifest_version,
            "knowledge_index_json": index_version,
        }

    if profile == "local":
        master = open(master_path, encoding="utf-8").read()
        mm = re.search(r"(?:Repository Version|repository version|Version)\s*[:=]\s*\*\*?v?([0-9.]+)", master)
        if not mm:
            mm = re.search(r"\bv([0-9]+\.[0-9]+)\b", master)
        if not mm:
            return "REPOSITORY_IDENTITY_UNVERIFIED", {"reason": "MASTER_PROMPT.md version unparseable in local profile"}
        if mm.group(1) != declared_version:
            return "REPOSITORY_VERSION_MISMATCH", {"repository": declared_version, "master_prompt": mm.group(1)}

    if expected_version and declared_version != expected_version.lstrip("v"):
        return "REPOSITORY_VERSION_MISMATCH", {
            "expected": expected_version,
            "found": declared_version,
            "reason": "Caller-specified expected version does not match repository's declared version — old/new prompt vs schema mismatch (P0-24).",
        }

    fingerprint = compute_fingerprint(root)
    return "REPOSITORY_VERIFIED", {
        "version": declared_version,
        "fingerprint": fingerprint,
        "checked_root": os.path.abspath(root),
    }


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    expected_version = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--profile=") else None
    profile = "distribution"
    for arg in sys.argv[2:]:
        if arg.startswith("--profile="):
            profile = arg.split("=",1)[1]
    status, details = run(root, expected_version, profile)
    print(f"STATUS: {status}")
    for k, v in details.items():
        print(f"  {k}: {v}")
    if status == "REPOSITORY_VERIFIED":
        print("\nResult: safe to proceed to Step 2 (Load Configuration). Generation may continue.")
        sys.exit(0)
    else:
        print(f"\nResult: execution_mode: BLOCKED — reason: {status}. Do NOT proceed to generation, "
              f"Smart Fallback, character resolution, or Islamic evidence retrieval. Per execution_modes.md "
              f"P0-1/P0-2, total or partial repository unavailability is never an Assisted Mode case.")
        sys.exit(1)


if __name__ == "__main__":
    main()
