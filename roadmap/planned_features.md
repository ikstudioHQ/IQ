# Planned Features

## Next (before scaling episode volume)
- **Batch 02 knowledge ingestion** — continue from the Knowledge Batch 01
  pilot slice (2026-08-05): find and verify real Hadith evidence for
  concept_justice (currently 0), and real Quran/Hadith for the other
  14 pilot concepts named in the Phase 2 brief (Sidq, Amanah, Rahmah,
  Sabr already partially covered, etc.) — following the exact same
  search→verify→cross-check→ingest process demonstrated on qv_006.
- Regenerate the fairness episode now that concept_justice clears the
  Smart Fallback bar — expected ASSISTED, not forced to Production
  (scholarly_reviewed still false). Not done in the knowledge-batch
  pass; a content-generation task, separate scope.
- Get a real qualified reviewer through the growing citation_verified
  entries (14 now, was 13) — same standing recommendation, larger now.
- Resync examples/ep_tawakkul_lost_toy/image_prompts.md's character
  descriptions against the current sources/characters/characters/*.md
  files — real drift found by episode_consistency_check.py in v2.15,
  not yet fixed.
- Add real Quran/Hadith evidence for 'adl (fairness/justice) —
  concept_justice exists with zero citable evidence; An-Nahl 16:90 is a
  strong real candidate but must be extracted properly per
  knowledge_builder_pipeline.md, not assumed. This directly unblocks
  the fairness episode that correctly BLOCKED in v2.15.
- Add child_paraphrase/educational_interpretation as distinct schema
  fields on phase2/data/islamic/*.json entries (currently only
  arabic_text + translation_simplified exist) — a schema change,
  intentionally not done in the v2.15 pass per its no-mass-data-edit rule.
- Add a real story conflict for each of the 4 concepts that still have
  no `recommended_default` combination (humility, prayer, community,
  charity — see `recommended_story_combinations.md`) — found honestly
  while building v2.13's story-combination feature, not force-fit.
- Get a qualified human reviewer to pass over the Islamic entries and
  the new v2.9 vocabulary/concept batch (see review_queue.json's
  batch_2026_08_02 entry) and flip human_reviewed to true (see
  review_workflow.md and verification_pipeline.md). Cheap now; expensive
  to retrofit after the dataset grows further.
- Populate competitor_benchmark.json with real data from the target
  competitor channel (COMPETITOR_STRATEGY.md Step 1).
- Resolve the Arabic-subtitle status discrepancy flagged in
  subtitle_prompt.md v2.7 (published_videos.json claims Arabic subtitles
  exist; languages.yaml marks Arabic status: planned, not active).

## Near-term
- Prompt regression testing wired to a real LLM API call (current
  tools/prompt_regression_test.py is a harness/scaffold only — see its
  header for what's still manual).
- Expand islamic_vocabulary.json, conflict_library.json,
  curiosity_hooks.json, ending_styles.json beyond their v2.7 seed sizes
  (8/12/6/5 entries respectively) as real episodes are produced — same
  incremental-not-mass-seed principle as the Islamic reference data.
- Fill in guest_appearances.json schema properly the first time a real
  collab episode happens (GUEST_CHARACTERS.md references it as
  create-on-first-use).

## Later
- Multi-language dictionary expansion beyond Arabic (French, Urdu word
  lists) — subtitle *spec* now supports ar/ur (v2.7), but the underlying
  vocabulary data for anything beyond English/Arabic is still thin.
- Merchandise design guides.
- Real analytics integration — creator_edits_log.json (v2.7) is a
  logging scaffold only; activation requires 20-30+ logged episodes
  per its own stated criteria.
