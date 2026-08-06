---
id: GOVERNANCE_CONFLICT_RESOLUTION
version: 1.0
status: production
depends_on: [AUTHORITY_HIERARCHY.md, authority_rules.md]
used_by: [AI Pipeline, Human Maintainers]
last_updated: 2026-07-30
---

# conflict_resolution.md — What To Do When Two Facts Disagree

This repository previously shipped with an unresolved conflict (two
incompatible character casts — see `ADR_001_character_system.md`) that
went undetected for at least one full audit cycle. This file exists so
that never happens silently again.

## The resolution procedure (in order)

1. **Identify which tier each conflicting source sits at**, per
   `AUTHORITY_HIERARCHY.md`: Constitution > Rules > Knowledge > Templates
   > Output.
2. **If the tiers differ**, the higher tier wins outright. Update or
   delete the lower-tier file to match. Log it in `CHANGELOG.md`.
3. **If the tiers are the same** (this is the dangerous case — it's what
   went wrong before): consult `authority_rules.md` for that domain's
   named source of truth. That file wins. The other is either deleted or
   rewritten to reference it.
4. **If `authority_rules.md` doesn't cover the domain** (a genuine gap):
   do not silently pick one. Stop and record the conflict as an open
   question in `phase1/docs/decisions/adr/` as a new ADR with status
   `proposed`, describing both options, and add a row to
   `authority_rules.md` once resolved. An AI agent encountering this
   case mid-pipeline should log it in `execution_state.json` per
   `MASTER_PROMPT.md`'s "Silent Drift Prevention" section and use the
   most conservative interpretation until a human resolves it.
5. **Never resolve a same-tier conflict by picking whichever file you
   happened to read first, or whichever seems more detailed.** Detail is
   not authority. (The old character conflict lost specifically because
   an agent following steps literally would have had no principled way
   to choose between two equally-detailed, equally-tier-3 sources — this
   procedure exists to remove that ambiguity going forward.)

## Detecting conflicts automatically
`tools/validate_repo.py` includes a best-effort authority-conflict scan
(duplicate character/topic/asset names across files, contradictory
version numbers for the same entity). It cannot catch semantic
contradictions ("RULES.md says X, a new file says not-X in different
words") — that class of conflict still requires a human read during
review. See `review_workflow.md`.

## Related Files
`AUTHORITY_HIERARCHY.md`, `phase1/docs/governance/authority_rules.md`,
`phase1/docs/decisions/adr/ADR_001_character_system.md`,
`phase1/docs/governance/review_workflow.md`
