---
id: GOVERNANCE_DEPRECATION_POLICY
version: 1.0
status: production
depends_on: [versioning_policy.md, authority_rules.md]
used_by: [AI Pipeline, Human Maintainers]
last_updated: 2026-07-30
---

# deprecation_policy.md — Retiring Old Knowledge

## When something should be deprecated
- A character design is replaced with a new locked version (e.g. a
  wardrobe update for a seasonal special).
- A curriculum topic is split into two more specific topics.
- A data schema changes shape and old entries no longer match.
- A file is superseded by a better-organized replacement (as
  `AUDIT_REPORT.md` / `FINAL_AUDIT_REPORT.md` were by `CHANGELOG.md` v2.3).

## The rule: retire, don't delete, unless the content is actively wrong
- **Supersede in place:** add a notice at the top of the old file
  pointing to the replacement (see the "Superseded notice" pattern used
  in `AUDIT_REPORT.md`). Keep the old file — it's historical record and
  may be cited by an old `episode_database.json` entry.
- **Version-lock old episodes to old data:** if `character_versions.json`
  moves a character to `v2.1`, episodes already published under `v2.0`
  keep referencing `v2.0` in their `character_versions_locked` field
  (see `character_version_lock.md`). Never retroactively change what a
  published episode was generated from.
- **Delete only when content is factually wrong or unsafe** (e.g. a
  disputed hadith entry that should never have been marked `verified`,
  or a broken/duplicate database entry). Deletions must be logged in
  `CHANGELOG.md` with the reason.
- **Never silently remove a file another file still references.** Run
  `tools/validate_repo.py` after any deletion — a new broken-reference
  error means something downstream still needs it.

## Per-item versioning (added v2.7)
The rules above cover whole-file/whole-character deprecation. Individual
data entries (a single dua, hadith, or vocabulary word) need the same
protection at smaller scale — a correction to one entry shouldn't
silently break an episode that already cited the old wording.

Convention for any entry that gets corrected after first publication:
```json
{
  "dua_id": "dua_003",
  "version": "v1.1",
  "deprecated": false,
  "superseded_by": null,
  "change_note": "v1.1: corrected transliteration spacing, 2026-08-01"
}
```
- Bump `version` on the entry itself (not just the file's version) when
  its content changes after being cited in a published episode.
- Set `deprecated: true` and `superseded_by: "<new_id>"` only if the
  entry is factually wrong and must be replaced with a different ID
  entirely (rare) — for wording corrections, just bump `version` in place
  and add a `change_note`; don't create a new ID for a minor fix.
- This field pair (`version`, `deprecated`) is additive — existing
  entries without it are treated as `deprecated: false` by default. Add
  it going forward on any entry you touch; retrofitting it onto all 37
  existing entries purely for the field's presence isn't worth the
  churn — add it when an entry actually needs its first correction.

## Deprecation checklist (apply before removing or replacing anything)
1. Search the whole repo for references to the file/entry being retired.
2. Update every reference to point at the replacement, or explicitly
   mark them historical if they describe a past state on purpose.
3. Add a `CHANGELOG.md` entry.
4. Run `tools/validate_repo.py` — must still `PASS`.
5. If the retired item was a `source of truth` per `authority_rules.md`,
   update that table in the same change.

## Related Files
`phase1/docs/governance/versioning_policy.md`,
`phase1/docs/governance/change_log_policy.md`, `CHANGELOG.md`
