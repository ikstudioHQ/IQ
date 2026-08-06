---
id: GOVERNANCE_REVIEW_WORKFLOW
version: 1.0
status: production
depends_on: [DESIGN_PRINCIPLES.md, RULES.md]
used_by: [AI Pipeline, Human Maintainers]
last_updated: 2026-07-30
---

# review_workflow.md — What Gets Reviewed, By Whom, Before Publish

## Three fields, not two — do not conflate them (updated v2.11)
Every Islamic reference entry (`phase2/data/islamic/*.json`, plus
`islamic_vocabulary.json` and `phase3/knowledge/concepts/*.json`) now
carries three separate fields, each answering a genuinely different
question, replacing the earlier two-field model (v2.4) and then the
single `human_reviewed` field (v2.9) — see `verification_pipeline.md`
for the full schema:

- **`citation_verified`** — does the entry name a real, specific source
  (not "Unknown source reference")? Checkable by anyone, no Islamic
  knowledge required.
- **`source_verified`** — has that named source actually been checked
  against the entry's content? Also checkable without Islamic knowledge
  for entries produced via `knowledge_builder_pipeline.md`'s documented
  extraction process — it's a "does the page really say this" check,
  not a "is this correct Islamically" check.
- **`scholarly_reviewed`** — has a real, qualified reviewer confirmed
  the entry is authentic and correctly applied? This is the only field
  of the three that requires actual Islamic domain knowledge. `false` on
  every entry in the repository as of this writing — nothing has been
  scholar-reviewed yet.

This split exists because the previous repository states either
overstated review (v2.3: every entry marked "verified" by
self-certification) or collapsed two different kinds of checking into
one ambiguous flag that implied the creator — who has no Islamic
background — was expected to personally clear it (v2.9's
`human_reviewed`). See `CHANGELOG.md` v2.4, v2.9, and v2.11.

## Review workflow by content type

| Content type | Who reviews | When | Gate |
|---|---|---|---|
| New Islamic reference entry (dua/hadith/Quran verse/etc.) | A qualified external reviewer (scholar, imam, or equivalent) — never the creator, who has no Islamic background | Before `scholarly_reviewed` is set `true` | Cannot ship in a published episode until `scholarly_reviewed: true` |
| New character or major visual redesign | Creator (human) | Before locking a new `locked_description_block` | Manual — this is a brand decision, not automatable |
| New episode script | Creator (human), spot-check for tone/brand fit only, not Islamic accuracy | Before upload | Recommended, not currently blocking — see `phase4/engine/quality/rubric.md` for the automatable portion |
| Repository structural changes (new files, schema changes) | Whoever makes the change | Before merge | Run `tools/validate_repo.py`; must show `PASS` with no new warnings introduced |
| Disputed religious opinions | External qualified reviewer, explicitly | Always, before use | Per `DESIGN_PRINCIPLES.md` non-negotiable #3 — never presented as settled fact |

## Practical note for a small/solo operation
A full scholarly board isn't realistic at this repository's current
scale (~117 entries across Islamic references, vocabulary, and concepts
as of v2.9's batch). The realistic minimum: get one qualified external
person to review the entries where `citation_verified: true` first
(these are the tractable, well-sourced ones — batch them together for
efficiency), before expanding the dataset further. Entries with
`citation_verified: false` need a source found before they're worth a
scholar's time at all — that's a creator-doable step (search for a real
citation, or remove the claim), not something to hand to a reviewer
as-is.

## Related Files
`phase1/docs/governance/authority_rules.md`,
`phase1/docs/governance/verification_pipeline.md`,
`phase2/data/islamic/*.json`, `DESIGN_PRINCIPLES.md`
