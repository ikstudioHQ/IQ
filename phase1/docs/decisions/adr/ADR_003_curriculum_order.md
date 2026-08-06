# ADR_003 — Curriculum Order: Allah → Creation → Animals → Gratitude → Parents → Prayer → Community → Leadership

**Status:** accepted
**Date:** originating design predates this repository's audit; formally recorded here

## Problem
Islamic educational content for ages 2-8 needs a defensible learning
sequence, not a randomly-ordered topic list, so that later episodes can
assume earlier concepts are already understood (per
`DESIGN_PRINCIPLES.md`: "never skip prerequisites").

## Decision
The curriculum follows a fixed dependency chain, documented in
`phase3/knowledge/curriculum/educational_dependency_graph.md` and enforced
via `phase2/data/database/topic_graph.json` prerequisite edges: awareness
of Allah as creator comes first (foundational, concrete-to-a-toddler
concept: "Allah made the world"), followed by creation/nature appreciation,
then animals (concrete, lovable, easy entry point for empathy), then
gratitude (an emotional/social concept built on top of noticing good
things), then kindness to parents (the child's most immediate relationship),
then prayer/worship practice (requires enough abstract-thinking readiness
that it's placed after the concrete-empathy stages), then community
(extending kindness beyond the family), then leadership (the most abstract,
placed last).

## Alternatives considered
1. **Calendar-driven ordering** (teach whatever fits Ramadan/Eid/etc. when
   it's seasonally relevant, ignore conceptual prerequisites). Rejected as
   the *sole* ordering principle — seasonal specials are still supported
   (`festivals.json`, `settings.yaml` future-proofing notes) but layered on
   top of the conceptual sequence, not replacing it.
2. **Alphabetical/topic-list ordering** (whatever's easiest to generate
   next). Rejected — directly violates the "never skip prerequisites"
   non-negotiable and produces a curriculum that looks unplanned to
   parents evaluating educational value.

## Consequences
- New topics added to `available_topics.json` must declare
  `prerequisites` against this chain (or an explicit branch of it) before
  they can be scheduled — `topic_graph.json` prerequisite validation in
  `MASTER_PROMPT.md` Step 13 depends on this being kept current.
- The chain is a starting skeleton, not exhaustive — expanding it (see the
  Knowledge Depth expansion work) should add branches consistent with this
  ordering logic, not replace the logic itself.

## Source
`phase3/knowledge/curriculum/educational_dependency_graph.md`,
`phase3/knowledge/curriculum/knowledge_curriculum.json`.
