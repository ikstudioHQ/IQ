---
id: PLANNING_RECOMMENDED_STORY_COMBINATIONS
version: 1.0
status: production
depends_on: [phase3/knowledge/concepts/, phase5/orchestration/planning/retrieval_ranking.md]
last_updated: 2026-08-03
---

# recommended_story_combinations.md — Starting Retrieval Ranking From a Strong Default

Every concept package in `phase3/knowledge/concepts/` now carries a
`recommended_default` field: a specific, real conflict + story pattern +
curiosity hook + ending style + driving emotion, chosen because it
genuinely fits that concept — not a placeholder.

## Why this exists
`retrieval_ranking.md` ranks candidates from scratch every time. That's
correct for avoiding staleness, but it means the very first episode ever
produced for a concept has no history to rank against — every candidate
starts at the same diversity-penalty baseline. `recommended_default`
gives the ranking engine a documented, sensible starting point instead
of an arbitrary first-match, while the diversity penalty still applies
normally on repeat use (an episode's second use of a concept will
naturally rank the default lower and surface an alternative).

## Format
```json
"recommended_default": {
  "conflict_id": "cf_001",
  "pattern_id": "pattern_001",
  "hook_id": "hook_002",
  "ending_id": "end_001",
  "emotion": "worry",
  "note": "..."
}
```

## Honest gaps — 4 of 20 concepts have no default yet
`concept_humility`, `concept_prayer`, `concept_community`, and
`concept_charity` have `"status": "not_yet_available"` instead of a
combination, because no entry in `conflict_library.json` (30 entries)
actually fits those concepts well. This was found, not hidden, while
building this feature — see `roadmap/planned_features.md` for the
tracked follow-up (add a real conflict for each before setting a
default, rather than force-fitting an existing one that doesn't
genuinely match).

## Related Files
`phase5/orchestration/planning/retrieval_ranking.md`,
`phase3/knowledge/story/conflict_library.json`,
`phase3/knowledge/concepts/`
