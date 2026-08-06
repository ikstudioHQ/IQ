# Validation Report

**Song:** song_003 · **Brand:** Islamic Kids Studio (@IslamicKidsHQ) · **Repository version:** v2.43 · **Last updated:** 2026-08-03 · **Confidence:** high (planned content) · **Reviewed:** false


execution_mode: production
production_ready: true (package complete; scholarly_reviewed remains false for all sources — separate gate per verification_pipeline.md; nothing is published)

## Registry alignment (verified against song_topic_bank.json)
- song_topic_id: song_003 — exists in the registry, production_readiness: READY_AFTER_CHARACTER_IMPORT
- primary_concept: concept_patience — concept file exists; learning goal used verbatim
- religious_evidence_ids: qv_007 — every id resolves in phase2/data/islamic/ (citation_verified: true)
- age_band: [6, 7] — lyrics/dialogue written to this band
- characters: char_001_zayd, char_003_ummi_layla, char_002_amira — all resolve in character_master_library.json
- typical_locations: loc_family_living_room
- scene_type/mood: effort_action / calm — applied per camera_language.json
- story_integration: position middle; intro dialogue True; outro dialogue True

## Package checks
- All 22 package files present and complete.
- Character lock (P0-5): core-cast locked blocks inlined verbatim in image_prompts.md and thumbnail.md.
- Claim binding: lyrics/dialogue contain no unattributed religious claims; islamic_refs.md and verification_report.md cite registered ids.
- Safety: no NEVER_GENERATE/BLOCK alias content (content_restrictions.json, content_scene_safety_registry.json).
- Duration: 98 lyric words ≈ 2:08 song + ~12s dialogue ≤ 2:30 hard cap.

## Honest notes
- scholarly_reviewed: false for all cited evidence (repository-wide state) — external qualified Islamic review required before publication.
- Voice providers null; voice identity IDs are the registered ones (no new IDs created).
- Secondary cast (no .md locked block yet) use their canonical prompts from character_master_library.json verbatim; the consistency checker's character-lock scope is the 6 core .md files — the full cast is declared by registry ID in episode_summary.md.
- Not published; reuse_tracking in the registry remains zero (no fabricated episode references).
