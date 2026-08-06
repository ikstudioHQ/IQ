# Validation Report

**Song:** song_015 · **Brand:** Islamic Kids Studio (@IslamicKidsHQ) · **Repository version:** v2.60 · **Last updated:** 2026-08-04 · **Confidence:** high (planned content) · **Reviewed:** false

execution_mode: production
production_ready: true (package complete; scholarly_reviewed remains false for all sources — separate gate per verification_pipeline.md; nothing is published)

## Registry alignment (verified against song_topic_bank.json)
- song_topic_id: song_015 — exists in the registry, production_readiness: READY_AFTER_CHARACTER_IMPORT
- primary_concept: concept_humility — concept file exists; learning goal used verbatim
- religious_evidence_ids: qv_014 — every id resolves in phase2/data/islamic/ (citation_verified: true)
- age_band: [6, 8] — lyrics/dialogue written to this band
- characters: char_001_zayd, char_010_yusuf, char_014_hamza — all resolve in character_master_library.json
- typical_locations: loc_neighborhood_park
- playlist_ids: pl_007_brave_hearts_and_big_feelings, pl_008_fair_hearts_and_growing_leaders
- roadmap category + dependencies: CORE_CONCEPT_ANCHOR | curriculum concept_gratitude, concept_kindness | prerequisites none
- scene_type/mood: group_family_moment / gentle — applied per camera_language.json
- story_integration: position middle; intro dialogue True; outro dialogue True

## Package checks
- All 22 package files present and complete.
- Character lock (P0-5): core-cast locked blocks inlined verbatim in image_prompts.md and thumbnail.md.
- Claim binding: lyrics/dialogue contain no unattributed religious claims; islamic_refs.md and verification_report.md cite registered ids.
- Safety: no NEVER_GENERATE/BLOCK alias content (content_restrictions.json, content_scene_safety_registry.json).
- Duration: fixed 2:08 song skeleton + ~12s dialogue ≤ 2:30 hard cap.

## Honest notes
- scholarly_reviewed: false for all cited evidence (repository-wide state) — external qualified Islamic review required before publication.
- Voice providers null; voice identity IDs are the registered ones (no new IDs created).
- Secondary cast (no .md locked block yet) use their canonical prompts from character_master_library.json verbatim; the consistency checker's character-lock scope is the 6 core .md files — the full cast is declared by registry ID in episode_summary.md.
- Not published; reuse_tracking in the registry remains zero (no fabricated episode references).
