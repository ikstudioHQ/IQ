# Repository Improvement Suggestions — generated 2026-08-04, from run ep_honesty_wallet_assisted

## Critical
- Extract luqatah (lost property) and truthfulness hadith from
  `en-p-al-arba3un-alnawawiia-abo-zakaria-annawawy-ppp.pdf` (40 Hadith
  an-Nawawi — already catalogued in `sources/islamic_books/CATALOG.md`
  as unextracted). Unblocks: any future "found item" or general-honesty
  topic, not just this one. Effort: ~30 min per
  `knowledge_builder_pipeline.md`'s documented process (same process
  already used successfully for dua_005/qv_004/prophet_yunus in v2.5).

## High
- Once the above hadith is extracted, add the specific "Allah rewards
  honesty" reward-framing claim if the source actually supports it
  directly — don't infer a reward claim from a general truthfulness
  hadith without checking the source says that specifically.

## Medium
- Add `t_honesty` to `available_topics.json` and `topic_graph.json` —
  `concept_honesty` already has a `recommended_age_range` (5-7) and a
  `recommended_default` combination ready to use once the topic node
  exists. Effort: ~10 min.
- Review whether `hd_002` (speak good or remain silent) should stay
  linked to `concept_honesty`'s `related_hadith` — this run confirmed
  it's a stretch for property-honesty claims specifically, even though
  it's a real fit for honesty-in-speech. Consider whether
  `concept_honesty` needs to split into a narrower speech-honesty vs.
  property-honesty distinction once more source material exists, or
  whether one broader concept remains the right scope.

## Low
- `conflict_library.json` has no entry specifically about finding a
  lost valuable item (as opposed to a promise, a shared item, or a shop
  item) — `cf_014` was close enough to reuse the spirit of for this
  episode, but a dedicated entry would be more precise for future runs.
