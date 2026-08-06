---
id: PLANNING_RETRIEVAL_RANKING
version: 1.0
status: production
depends_on: [phase2/data/config/retrieval_ranking_weights.yaml, phase2/data/database/world_state.json]
used_by: [AI Pipeline]
last_updated: 2026-08-02
---

# retrieval_ranking.md — Choosing the BEST Candidate, Not Just the First Match

Every knowledge-selection point in the pipeline (which verse, which
hadith, which dua, which conflict, which curiosity hook, which ending
style, which story pattern) currently just returns whatever matches a
filter. This engine replaces "find matches" with "rank matches and
return the top 3," using weights from
`phase2/data/config/retrieval_ranking_weights.yaml` — tunable without
touching any prompt or code.

## Where this runs
`MASTER_PROMPT.md` Step 16 (Plan Episode), for each of: Islamic
reference selection (Step 14's candidates), conflict selection
(`conflict_library.json`), curiosity hook selection
(`curiosity_hooks.json`), ending style selection
(`ending_styles.json`), and story pattern selection
(`story_patterns.json`). Same algorithm, same weights file, applied at
each selection point with the dimension definitions adapted to what's
being ranked (see per-type notes below).

## Scoring formula
For each candidate, compute:
```
raw_score = (topic_relevance_score * topic_relevance_weight
           + age_match_score * age_match_weight
           + educational_value_score * educational_value_weight
           + authenticity_score * authenticity_weight
           + source_confidence_score * source_confidence_weight) / 100

diversity_multiplier = 1 + (diversity_penalty_percent / 100)
# diversity_penalty_percent comes from the diversity_penalty table in
# the weights file, looked up by the candidate's recent-usage status

final_score = raw_score * diversity_multiplier
```
Each per-dimension score (`topic_relevance_score`, etc.) is 0-100,
scored per the sub-rules below. Diversity is applied as a multiplier
on the combined score, not as one more additive dimension — this makes
a heavily-overused candidate mathematically unable to win purely on
being the "best" match on paper, which is the actual point (a perfect
match used 5 episodes running should still lose to a good match used
zero times).

## Per-dimension scoring rules
- **topic_relevance**: 100 if the candidate's tagged concept/category
  exactly matches the resolved topic's concept; 60 if it's in a related
  category (e.g. `concept_gratitude` candidate considered for a
  `concept_honesty` topic because both pair with the same conflict); 0
  if unrelated (shouldn't reach ranking at all — filtered out earlier).
- **age_match**: 100 if the target age falls inside the candidate's
  `age_range`/`age_appropriate` field; 50 if within 1 year of the range
  boundary; 0 if clearly outside it.
- **educational_value**: 100 if the candidate has a populated
  `learning_objective`/`key_lesson` field; 50 if implied but not
  explicit; 0 if absent.
- **authenticity**: derived from `authenticity_level` /
  `scholarly_review_status` field — 100 for `"verified"` with a named
  `primary_source` (not "Unknown source reference" — see
  `knowledge_builder_pipeline.md`), 40 for `"verified"` with an unnamed
  source, 0 otherwise.
- **source_confidence**: 100 if `scholarly_reviewed: true`, 0 if `false`.
  Deliberately binary and low-weighted (5% default) — see the weights
  file's note on why this doesn't dominate the ranking by itself.

## Diversity lookup by candidate type
- **Islamic references** (dua/hadith/verse/prophet): check
  `world_state.json`'s `episode_chronology` for the `_id` appearing in
  the last 1/3 episodes, or count total appearances.
- **Conflicts**: check `world_state.json`'s `conflict_usage` (added
  v2.21) for total appearances across ALL concepts, not just this one.
- **Hooks/endings**: same pattern — check the last-used `hook_id`/
  `ending_id` in chronology.
- **Patterns — cross-concept total, not just recency (fixed v2.21):**
  the original spec only checked whether a pattern was *recently* used
  by *this* concept, which cannot catch a different concept
  independently choosing the same generically-fitting pattern — exactly
  the failure that let `pattern_002` land in 3 of 8 early episodes
  (Patience, Good Speech, Self-Control), none of which had ever used it
  before individually. Check `world_state.json`'s `pattern_usage` (added
  v2.21) for the TOTAL count across the whole repository, regardless of
  which concept used it, before treating a `recommended_default`
  pattern as available. A pattern already used 2+ times total gets a
  real penalty even on a concept encountering it for the first time.
- **Concepts**: use `world_state.json`'s `concepts_taught.times_used`
  directly (already tracked since v2.7's Moral Progression addition).
- **`recommended_default` is a seed, never an unconditional winner**
  (clarified v2.21): if the recommended pattern/conflict is already
  heavily used repository-wide, rank it against the concept's other
  `related_conflicts`/available patterns normally — don't skip ranking
  just because a default exists.

## Output
Present the top 3 ranked candidates with their final scores and a
one-line reason each (matching `topic_planner.md`'s "never auto-select,
present as a numbered choice" pattern) — unless running inside the fully
automatic `MASTER_PROMPT.md` pipeline for a single-topic generation, in
which case take the #1 ranked candidate automatically but log all 3
scores in `generation_log.json` so the ranking is auditable after the
fact, not just asserted.

## Pattern Fallback Mechanism (added v2.22)
Every concept now carries `recommended_default` (primary pattern) AND
`alternative_patterns` (a ranked list of real, conflict-paired
alternates — added v2.22, extending the existing concept schema, not a
new engine). Selection logic:

1. Score the primary pattern: `semantic_fit_score * diversity_multiplier(pattern_usage[primary])`.
2. Score each alternative the same way against ITS OWN paired conflict
   (an alternative is only valid together with the conflict it was
   built for — never mix an alternate pattern with the primary's conflict).
3. Select the highest score. Primary wins ties (rule: "primary remains
   preferred when usage is healthy").
4. If the primary's score is clearly weaker than an alternative's
   (diversity penalty made the difference, not semantic fit), reroute —
   log `fallback_triggered: true` with the reason.
5. If no alternative exists and the primary is heavily overused, that's
   an honest `fail: no_suitable_alternative` — never fabricate one.
6. Never let diversity override semantic fit — an alternative is only
   ever a candidate because it was already vetted as a real fit for its
   paired conflict, not picked for being merely "different."

## Related Files
`phase2/data/config/retrieval_ranking_weights.yaml`,
`phase2/data/database/world_state.json`,
`phase5/orchestration/planning/topic_planner.md`,
`phase4/engine/teaching/teaching_strategy.json`
