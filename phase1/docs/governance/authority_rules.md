---
id: GOVERNANCE_AUTHORITY_RULES
version: 1.0
status: production
depends_on: [AUTHORITY_HIERARCHY.md, DESIGN_PRINCIPLES.md]
used_by: [AI Pipeline, Human Maintainers]
last_updated: 2026-07-30
---

# authority_rules.md — Who Decides What

This expands `AUTHORITY_HIERARCHY.md` (which gives the five-tier priority
order) into concrete, per-domain ownership: which single file is the
**source of truth** for each kind of fact in this repository. When two
files seem to describe the same thing, the one listed here wins — the
other should either be deleted or rewritten to reference this one instead
of restating it.

## Source-of-truth table

| Domain | Source of truth | Everything else in this domain must... |
|---|---|---|
| Non-negotiable philosophy/quality rules | `DESIGN_PRINCIPLES.md` | ...cite it, never restate or reinterpret its rules |
| Conflict priority order | `AUTHORITY_HIERARCHY.md` | ...defer to it, never invent a new priority order locally |
| Character visual identity | `sources/characters/characters/*.md` (locked description blocks) | ...copy the block verbatim or reference the file; never paraphrase a character's appearance elsewhere |
| Character personality/relationships/continuity | `phase3/knowledge/characters/knowledge_characters.json` | ...treat this as the only place personality/relationship facts are declared |
| Islamic reference data (Quran, hadith, duas, etc.) | `phase2/data/islamic/*.json` | ...cite the `_id` from these files; never restate translated text elsewhere |
| Curriculum sequencing | `phase3/knowledge/curriculum/knowledge_curriculum.json` + `phase2/data/database/topic_graph.json` | ...treat prerequisite/age data here as final |
| World/environment descriptions | `phase3/knowledge/world/knowledge_world.json` | ...reference `env_id`, never redescribe a location inline |
| Pronunciation | `phase2/data/language/pronunciation_dictionary.json` | ...never invent a pronunciation elsewhere |
| Brand identity (colors, logo, handle) | `phase1/docs/brand/BRAND.md` | ...reference it, never restate the palette with different values |
| Current production pointer (what episode/series is active right now) | `phase2/data/database/current_state.json` | ...this is the only file allowed to say "current" |
| Accumulated continuity history (what's happened across all episodes so far) | `phase2/data/database/world_state.json` | ...append to it; don't keep parallel continuity logs elsewhere |
| Quality bar / scoring | `phase4/engine/quality/rubric.md` | ...checklists (`qa_checklist.md`, `VALIDATION_MATRIX.md`) implement it, they don't redefine "good" |
| Competitor/format strategy | `phase1/docs/seo/COMPETITOR_STRATEGY.md` | ...reference it; don't duplicate its reasoning in other SEO files |

## Rule for adding anything new
Before creating a new file that stores a fact, check this table. If a
domain already has a source of truth, add to that file — don't create a
second one. If the new fact genuinely doesn't fit an existing domain, add
a new row here in the same pull request that adds the file, so the table
never falls out of date.

## Related Files
`AUTHORITY_HIERARCHY.md`, `DESIGN_PRINCIPLES.md`, `phase1/docs/governance/conflict_resolution.md`
