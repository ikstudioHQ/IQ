---
id: GOVERNANCE_CHANGE_LOG_POLICY
version: 1.0
status: production
depends_on: [versioning_policy.md]
used_by: [AI Pipeline, Human Maintainers]
last_updated: 2026-07-30
---

# change_log_policy.md — What Belongs In CHANGELOG.md

## The standard this repository now holds itself to
Every `CHANGELOG.md` entry must be **independently verifiable**, not
narrated. Before v2.3, entries here claimed things like "Zero
contradictions confirmed" and "100/100" without a script or independent
check backing them up — and those specific claims turned out to be
false. That failure mode is what this policy exists to prevent.

## Rule: no unverifiable superlatives
Do not write "zero broken references," "100% consistent," "fully
verified," or similar absolute claims in a changelog entry unless:
- A specific tool run backs it up (name the tool and, ideally, paste or
  summarize its output), **or**
- The claim is scoped and checkable by a human in under a minute (e.g.
  "all 6 character files now use the same cast" is checkable by
  grep; "zero contradictions repository-wide" is not, and should never
  be written again).

## Required entry format
```
## v<X.Y> — <short description> (<date>)
- <What changed, specifically, with file paths>
- <Why, if not obvious>
- <How it was verified — tool name + result, or "manual read of X">
```

## What triggers a new entry
- Any fix to a broken reference, malformed data, or contradiction.
- Any new file that becomes a "source of truth" per `authority_rules.md`.
- Any version bump (see `versioning_policy.md`).
- Any deprecation (see `deprecation_policy.md`).
- Any change to `DESIGN_PRINCIPLES.md` non-negotiables (rare, high-scrutiny).

## What does not need an entry
- Adding a new Islamic reference, character interaction, or environment
  within an existing schema (that's routine content growth — log it in
  `phase2/data/database/generation_log.json` instead, not `CHANGELOG.md`).

## Related Files
`CHANGELOG.md`, `phase1/docs/governance/versioning_policy.md`, `tools/validate_repo.py`
