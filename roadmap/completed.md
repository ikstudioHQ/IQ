# Completed

## v2.25 (2026-08-05) — RELIGIOUS DATA CLEANUP INCOMPLETE (real, not padded)
- Recomputed and confirmed the real uncited count (21/59) before acting
- Fixed qv_001-003 (were excerpts mislabeled as complete verses)
- Fixed sun_001-002 (real Bukhari 5376/Muslim 2022 citation)
- 16 remain honestly uncited, queued in human_review_queue.md
- CONTINUATION MARKER: next session verify sun_003-005, mann_001-008,
  fest_001-003, companion_aisha, companion_ali — do not redo qv_001-003/
  sun_001-002, already real-cited this session

## v2.24 (2026-08-05) — DATA READY FOR CHARACTER INTEGRATION
- 9 real vocab mislinks fixed (prayer/mercy words existed, never linked)
- hd_014 added (Mercy's second evidence source)
- Vocabulary 110→113, Coverage 13 STRONG/9 ADEQUATE (was 11/11)
- Episode topic bank: 44 real grounded topics
- Song topic bank: 22 topics
- 15-concept retrieval regression clean, restriction audit clean

## v2.23 (2026-08-05) — READY FOR CHARACTER ASSET PRODUCTION
- qv_016 primary-reverified (found and fixed a truncation bug)
- Justice/Community strengthened to 2 evidence types each
- Vocabulary 90→110
- Character schema extended with granular asset/voice fields (additive, empty)
- Coverage matrix: 11 STRONG/11 ADEQUATE, 0 THIN/BLOCKED (was 7/15)
- 10-concept retrieval regression clean

## v2.22 (2026-08-05) — ARCHITECTURE FROZEN
- Pattern fallback mechanism complete: alternative_patterns on all 22
  concepts, proven with real 30-run simulation (53% fallback activation)
- Community concept strengthened (Quran 4:36)
- Character schema extended additively for future asset library
- Song/nasheed safety coverage confirmed (no gap, no new system needed)
- 5 final multi-type stress episodes (story/manners/song/community/family)
- No genuine architecture blocker found — declared FROZEN

## v2.21 (2026-08-05)
- Diagnosed pattern-diversity defect root cause: world_state.json had
  no pattern/conflict usage tracking (8/22 concepts collided on
  pattern_002, not 3 as first estimated)
- Fixed: added tracking fields, extended retrieval_ranking.md's
  diversity check, redistributed 12 concepts' recommended_default
  (max concentration 8→3)
- Real 20-run simulation executed, found a genuine deeper gap
  (no alternate-pattern fallback) — reported, not rushed-fixed
- 5 new episodes on corrected defaults: zero pattern collisions

## v2.20 (2026-08-05)
- Vocabulary 50→90, Conflicts 50→60
- 22-concept audit: 7 STRONG, 15 ADEQUATE, 0 THIN, 0 BLOCKED — coverage
  matrix saved
- 5 stress-test episodes with unmodified real retrieval — found and
  reported a genuine pattern_002 over-selection defect (3 of 8 episodes)
- Fixed missing semantic_support classification for 5 concepts

## v2.19 (2026-08-05)
- All 4 Prophets now real-cited (prophet_ibr, prophet_muh reverified;
  was 1 of 4 before)
- Story patterns 5→13, structurally distinct, verified against
  existing patterns before adding
- Conflicts 30→50, filling real gaps for 12 previously-underlinked
  concepts (prayer, cleanliness, community, perseverance, humility,
  courage, friendship, good_speech, charity, compassion_for_animals,
  self_control, trustworthiness)
- Retrieval-diversity fix: 12 concepts moved off the pattern_002
  default onto genuinely distinct patterns

## v2.18 (2026-08-05)
- Knowledge-expansion checkpoint: all 22 concept files now have real
  evidence (was several empty)
- Prophet Nuh reverified and cited (Quran 29:14)
- New Dua (leaving-home, Abu Dawud 5095)
- Quran 9→15, Hadith 8→12, Duas 6→7

## v2.17 (2026-08-05)
- All 23 regression letters executed with real fixtures (up from 17)
- Packaging hard-gated on episode_consistency_check.py — real gap found
  via rollback testing, closed
- 3 new checkers: semantic overreach (I/J), paraphrase-as-quotation (N),
  character resolution (E)
- Removed a dangerous exemption in fabricated-source-ID detection (K/M)
- 6 real false-positive bugs found and fixed via anti-false-pass testing
- Zayd/Amira character-lock drift fixed in both proof episodes

## v2.16 (2026-08-05)
- 17/23 regression letters proven, Zayd drift resolved
- Excluded-claim propagation into SEO/Shorts proven caught
- production_ready invariants (T/U), fabricated-source-ID detection (K/M)
- prompt-injection immunity confirmed, clean-repo artifacts removed
- child_paraphrase/educational_interpretation fields added to 2 real entries

## v2.15 (2026-08-05)
- Repository Presence Guard (tools/preflight_check.py) — hard blocks
  before generation on absent/incomplete/version-mismatched repository
- Cross-field Quran/Hadith SOURCE_MISMATCH detection in validate_repo.py
- Protected-source mutation detection + character-lock byte verification
  (tools/episode_consistency_check.py)
- Semantic claim support levels + controlled status vocabulary in
  verification_pipeline.md
- Real bugs found and fixed: concept_justice's mislinked vocabulary
  reference; tawakkul proof episode's character-lock drift (logged,
  not yet resynced)
- Real BLOCKED regression result for fairness episode against actual
  repository data (examples/ep_fairness_v2_15_regression/)

## v2.14 (2026-08-04)
- Three execution modes (Production/Assisted/Blocked) replace binary
  PASS/BLOCK at MASTER_PROMPT.md Step 14
- Smart Fallback, Auto Duration Correction, Draft Curriculum Mode
- Extended missing_knowledge_report.md schema + new
  repository_improvement_suggestions.md output
- All three modes demonstrated with real generated episodes in examples/

## v2.13 (2026-08-03)
- Completed real knowledge-graph cross-links (concept↔hadith↔manners↔
  prophets, bidirectional concept↔conflict consistency)
- Found and fixed a real mislabel (concept_cleanliness ↔ wrong conflict)
- Added recommended_default story combinations to all 20 concepts
  (4 honestly marked not_yet_available rather than force-fit)
- Extended validator: circular-reference + empty-required-field checks
- Extended cinematography metadata: color_palette, depth_of_field

## v2.12 (2026-08-03)
- Fixed 17 stale hardcoded 'v1.1' version references in MASTER_PROMPT.md's
  body, found by an independent external audit
- Added MASTER_PROMPT.md header check + stale-version-string scanning to
  tools/validate_repo.py so this class of bug is caught automatically
- Corrected a real arithmetic error in the v2.11 changelog (117 → 107)

## v2.11 (2026-08-03)
- Single human_reviewed flag replaced with three independent fields
  (citation_verified, source_verified, scholarly_reviewed) across all
  117 Islamic/vocabulary/concept entries
- verification_report.md upgraded to full per-claim Evidence & Risk
  schema with an Evidence Summary dashboard

## v2.10 (2026-08-03)
- Human Review Pipeline replaced with Evidence & Verification Pipeline —
  correctly splits creator-doable citation-completeness checking from
  external-reviewer-only scholarly accuracy checking
- verification_report.md added as required per-episode output
- MASTER_PROMPT.md output numbering cleanup

## v2.9 (2026-08-02)
- Cinematography Intelligence (structured JSON, 6 scene types)
- Human Review Pipeline (review_queue.json + enforcement in package_episode.py)
- First real end-to-end proof episode (examples/ep_tawakkul_lost_toy/)
  — auto-reject gate correctly fired on it, documented honestly
- Arabic subtitle inconsistency resolved (not just flagged)
- Knowledge base batch: vocabulary 8→50, conflicts 12→30, concepts 3→20

## v2.8 (2026-08-02)
- Retrieval Ranking Engine (6 weighted dimensions, configurable weights)
- Diversity penalty (multiplier-based, prevents overused candidates
  from winning purely on-paper matches)
- teaching_strategy.md converted to teaching_strategy.json (structured
  data over prose, per direct feedback)

## v2.7 (2026-08-01)
- Islamic Concept Database (3 concept packages)
- Islamic Vocabulary Database
- Story Conflict Library + Story Patterns (the latter previously
  believed to exist but didn't — built for real this round)
- Curiosity Hooks Database, Ending Styles Database, Emotion Database
- Topic Planner + Curriculum Expansion Engine extension
- Teaching Strategy Engine
- Real Shorts generator (shorts_prompt.md) + Multi-Story profile
- Thumbnail Intelligence rules (extended thumbnail_prompt.md)
- Content Quality auto-reject gate (extended rubric.md)
- Moral Progression tracking (extended world_state.json + MASTER_PROMPT Step 16)
- Per-item knowledge versioning convention (extended deprecation_policy.md)
- Educational review questions (extended curriculum)
- Knowledge Builder Pipeline (formalized from real book-extraction work)
- Hijri calendar schedule (real, web-verified 2027 dates)
- Multi-language subtitle spec (ar/ur), surfaced a real Arabic-status
  inconsistency between published_videos.json and languages.yaml
- Dormant feedback/edit logging scaffold (creator_edits_log.json)
- Community/governance docs: MODERATION.md, PARENT_TRUST_PAGE.md,
  SPONSORSHIP_POLICY.md, dispute_response.md, GUEST_CHARACTERS.md

## v2.6 (2026-07-31)
- Made image_prompts.md / animation_directions.md self-contained,
  copy-paste-ready blocks for external tools (Gemini, Meta AI, etc.)
- Added lyrics_and_song.md output for external audio/song generation
- Fixed a 4-file filename-mismatch bug between MASTER_PROMPT.md's output
  list and the actual package/zip filenames

## v2.5 (2026-07-31)
- Extracted real, page-cited Islamic content from creator-provided books
  (Hisn al-Muslim, Ibn Kathir's Stories of the Prophets) via OCR/text
  extraction — added dua_005, dua_006, qv_004, qv_005, prophet_yunus
- Added t_tawakkul curriculum topic, unblocking a previously-halted
  pipeline run
- Fixed a real duplicate active/planned topic-status bug
- Backfilled world_state.json for already-published episodes
- Made the governance tier explicit in AUTHORITY_HIERARCHY.md
- Added MULTI_CHANNEL.md and sources/islamic_books/CATALOG.md (including
  a real CC NonCommercial-NoDerivs licensing flag on the Quran
  translation files)

## v2.4 (2026-07-30)
- Governance layer (phase1/docs/governance/)
- Architectural Decision Records (phase1/docs/decisions/adr/)
- Quality Rubric Engine (phase4/engine/quality/rubric.md)
- World State Engine (phase2/data/database/world_state.json)
- Failure Knowledge Base (phase3/knowledge/failures/)
- Child Development Matrix (phase1/docs/curriculum/CHILD_DEVELOPMENT_MATRIX.md)
- Extended validator (duplicate IDs, version consistency, unreviewed Islamic content)
- Prompt regression test harness (tools/prompt_regression_test.py)
- human_reviewed field added to all Islamic reference entries

## v2.3 (2026-07-30)
- Character system unification (Zayd/Amira cast made sole canonical system) — see ADR_001
- Broken reference fixes, YAML bug fixes, version unification
- tools/validate_repo.py, tools/package_episode.py
- phase1/docs/seo/COMPETITOR_STRATEGY.md
