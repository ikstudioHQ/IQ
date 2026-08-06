---
id: PLANNING_TOPIC_PLANNER
version: 1.0
status: production
depends_on: [phase2/data/database/available_topics.json, phase2/data/database/topic_graph.json, phase2/data/database/completed_topics.json, phase3/knowledge/curriculum/knowledge_curriculum.json]
used_by: [AI Pipeline, Human Maintainers]
last_updated: 2026-08-01
---

# topic_planner.md — What To Produce Next

Answers "what should the next episode be about," not "how to write it."
This is an algorithm spec — a coding agent runs this logic when the
creator asks "what should I make next?" rather than giving a specific
topic. It does not run automatically as part of `MASTER_PROMPT.md`'s
per-episode pipeline (that still requires an explicit topic per
`AUTOMATIC STEP 9`) — this is a separate, on-demand planning step.

## Algorithm
1. Load `completed_topics.json` (what's shipped) and `available_topics.json`
   (what's defined, active or not).
2. Compute the set of topics in `available_topics.json` whose
   `prerequisites` are all satisfied by `completed_topics.json` but which
   are not themselves in `completed_topics.json` — these are
   **immediately producible next**.
3. Rank that set by:
   - **Curriculum balance** — prefer a topic from an `islamic_concepts`
     category not recently covered (check the last 3 entries in
     `world_state.json`'s `episode_chronology`, cross-referenced against
     `available_topics.json`'s `category` field).
   - **Character usage balance** — prefer a topic whose likely cast
     hasn't been the lead in the last 2 episodes (per
     `world_state.json`'s `character_lessons_learned`).
   - **Seasonal relevance** — if within 30 days of a date in
     `festivals.json`, surface the matching seasonal topic
     (`t_ramadan_intro`, `t_eid_joy`) regardless of the above ranking.
4. Present the top 3 as suggestions, each with: topic title, why it
   ranked (one line), and its prerequisites (confirming they're met).
5. Never auto-select — always present as a numbered choice for the
   creator to confirm, consistent with `MASTER_PROMPT.md`'s Silent Drift
   Prevention principle (a planning suggestion is not the same as a
   topic instruction).

## Example output
```
Completed: t_intro, t_morning_dua, t_parents

Suggested next (prerequisites met):
1. t_eating_dua — "Dua Before Eating" — not yet covered, simple next step for age 3-5
2. t_prophets_intro — "Introduction to Prophets" — unblocks the whole
   Prophets branch (t_prophet_nuh, t_tawakkul both wait on this)
3. t_ramadan_intro — "What is Ramadan?" — only if within 30 days of Ramadan
```

## Curriculum Expansion Engine (extension of the same algorithm)
When step 2 above produces an empty or very small set (few/no
immediately-producible topics), that's a signal the curriculum has a
gap — not that production should stop. In that case:
1. Look at `knowledge_curriculum.json`'s `age_groups[].islamic_concepts`
   for the next age band and check whether each concept has a matching
   `topic_id` in `available_topics.json`. Concepts without one are
   candidate new topics.
2. Suggest these as new topic definitions to add (following the pattern
   in `ADR_001` through `ADR_004` for how new structural additions get
   documented), not as episodes to generate directly — a new topic needs
   its own prerequisites, age range, and supporting Islamic references
   (per `authority_rules.md`) before it's producible.

## Related Files
`phase2/data/database/available_topics.json`,
`phase2/data/database/topic_graph.json`,
`phase2/data/database/completed_topics.json`,
`phase2/data/database/world_state.json`,
`phase2/data/islamic/festivals.json`
