---
id: GOVERNANCE_VERSIONING_POLICY
version: 1.0
status: production
depends_on: [VERSION_COMPATIBILITY.md]
used_by: [AI Pipeline, Human Maintainers]
last_updated: 2026-07-30
---

# versioning_policy.md — One Version Number, Everywhere

## The problem this fixes
Before v2.3, this repository had six-plus files independently claiming
different "current" versions (1.1, 2.0, 2.1, 2.2) with no single source
of truth. That is now explicitly forbidden.

## The rule
- **`VERSION_COMPATIBILITY.md` is the only file allowed to declare "the
  current repository version."** Every other file's `version:` /
  `"version"` field must match it exactly.
- Character module version (`sources/characters/character_index.json`
  `"version": "2.0"`) is a separate, independently-tracked number — it
  versions the character *module*, not the whole repository. This is
  intentional (a module can be more stable than the repo around it) and
  is documented here so it isn't mistaken for an inconsistency: repo
  version and module version are different numbers by design, but both
  must be internally consistent within their own scope.
- When you bump the repository version:
  1. Update `VERSION_COMPATIBILITY.md` first.
  2. Update `repository_manifest.json`, `MASTER_PROMPT.md` header,
     `phase2/data/config/settings.yaml`, `knowledge_index.json`,
     `DESIGN_PRINCIPLES.md` header, in the same change.
  3. Run `tools/validate_repo.py` (its version-consistency check — see
     `CHANGELOG.md` v2.4 — will fail the build if any of these drift).
  4. Add the `CHANGELOG.md` entry.
- **Per-character and per-asset versions are independent** of the
  repository version (e.g. `Zayd v2.0` the character design vs. `v2.4`
  the repository). Don't conflate them — see
  `phase2/data/database/character_version_lock.md`.

## Per-file frontmatter version labels are NOT the repository version (clarified v2.12)
Most `.md` files in this repository carry a `version: 1.1` field in
their YAML frontmatter, or a `> Version: 1.1 | ...` header line — this
is a static per-document authoring label from before
`VERSION_COMPATIBILITY.md` existed, not a live pointer to the current
repository version. These labels are not required to track repository
version bumps, and `tools/validate_repo.py`'s stale-version scan
deliberately skips the first 12 lines of every file (the frontmatter
zone) for this reason.

**What IS a bug, and was found by an external audit in v2.12**: hardcoded
version numbers inside a document's *body*, especially inside
instructions telling an AI agent to check or confirm a specific version
number (e.g. "Confirm version tracking (`v1.1`)"). Those are live
instructions, not authoring labels, and they must reference
`VERSION_COMPATIBILITY.md` dynamically rather than hardcoding a number —
Historical v2.12 repairs removed hard-coded operational version instructions. The retired engine-level `master_prompt.md` is not a current authority; current bootstrap authority is documented by the repository hierarchy and the local-only MASTER boundary.

## Related Files
`VERSION_COMPATIBILITY.md`, `CHANGELOG.md`,
`phase1/docs/governance/change_log_policy.md`
