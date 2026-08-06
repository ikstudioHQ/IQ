---
id: DECISIONS_DECISION
version: 1.1
status: production
depends_on: [MASTER.md, BRAND.md]
used_by: [AI Pipeline, Content Generator]
last_updated: 2026-07-30
---

# DECISION — Decision Framework

## Purpose
Defines how AI makes decisions about story direction, character actions, curriculum choices, content approvals.

## Major Architectural Decisions
Repository-level architecture decisions (character system, visual style
strategy, curriculum ordering, prompt orchestration strategy) are recorded
as individual Architectural Decision Records in
`phase1/docs/decisions/adr/` — one file per decision, each with Problem,
Decision, Alternatives Considered, Consequences, and Source. Start with
`phase1/docs/decisions/adr/ADR_001_character_system.md`. This file
(`DECISION.md`) remains the framework for smaller, per-episode content
decisions (below); it does not duplicate the ADRs.

## Categories
Story direction, character action, curriculum choice, Islamic reference, visual style, voice tone, SEO approach.

## AI Instructions
Reference relevant domain document before deciding. Confirm brand alignment, age appropriateness, curriculum progression.

## Decision Log (Rich Format)

Every major content decision must include:
- **Why:** The reasoning behind the choice.
- **Alternatives:** What other options were considered.
- **Tradeoffs:** The benefits and costs of the chosen option.
- **Impact:** How this decision affects future episodes, characters, curriculum, or brand consistency.
- **Source:** Which document or research supports this decision.
- **Confidence:** `verified`, `high`, `medium`, or `low`.
- **Review Status:** `true` or `false`.
- **Timestamp:** When the decision was made.

## Example Decision Entries

### Decision: Original Character Design Philosophy
- **Why:** Original characters avoid copyright infringement and create lasting emotional connections with children.
- **Alternatives:** Licensing existing characters; creating generic unnamed figures.
- **Tradeoffs:** Original design requires more time but builds brand identity; licensed characters are faster but expensive and restricted.
- **Impact:** Every future episode must use these character designs. Merchandise and animation must match.
- **Source:** `CHARACTER.md`, `knowledge_characters.json`
- **Confidence:** `verified`
- **Review Status:** `true`
- **Timestamp:** `2026-07-30`

### Decision: Age-Based Curriculum Progression (2-8)
- **Why:** Children at different ages have different cognitive, emotional, and spiritual needs.
- **Alternatives:** Single curriculum for all ages; no structured progression.
- **Tradeoffs:** Age-based design requires more planning but ensures age-appropriate education; single curriculum is simpler but ineffective.
- **Impact:** Every episode must confirm age prerequisites. Topic graph must be maintained.
- **Source:** `CURRICULUM.md`, `knowledge_curriculum.json`
- **Confidence:** `verified`
- **Review Status:** `true`
- **Timestamp:** `2026-07-30`

## Related Files
MASTER.md, STORY.md, CURRICULUM.md, ISLAMIC.md
