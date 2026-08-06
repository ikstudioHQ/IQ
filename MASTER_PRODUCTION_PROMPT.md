# MASTER PRODUCTION PROMPT — Islamic Kids Studio
Authoritative, reusable prompt for generating a complete season. Controls the existing repaired implementation (Phases 1–8, blocker-repaired). Does not reimplement any of its logic — every instruction below invokes something that already exists in the codebase.

---

## HOW TO USE THIS PROMPT

Give the system a request in this shape:

> "Generate a 30-episode season, approximately 10 minutes per episode, for children aged 5–8."

Optionally specify a theme/topic, language, or a different episode count/duration. If you omit any of these, use sensible defaults and state what you chose — never block on a missing optional field.

The system executing this prompt must call the real production entry point — `generate_season()` in `tools/orchestration/season_orchestrator.py` — with:
- `theme` (from the request, or a reasonable default derived from context if none given)
- `episode_count` (from the request, default 30 if unspecified)
- `episode_duration_minutes` (from the request, default 10 if unspecified)
- `language` (from the request, default English if unspecified)
- `target_age` (from the request, default "5-8" if unspecified)
- `season_id` — the software does not generate this on its own; derive a stable, unique identifier (e.g. a slug of the theme plus a date) and reuse the *same* `season_id` on every subsequent call for this season, since re-using it is what makes production resumable rather than a restart.

Do not ask the requester to supply anything beyond theme/episode count/duration/language/target age. Everything else in this document is an instruction to the *system*, not a question for the requester.

---

## WHAT TO DO — IN ORDER, USING WHAT ALREADY EXISTS

1. **Call `generate_season()`** with the inputs above. This alone drives season planning, episode authoring requests, Story State updates, clip planning, continuity resolution, safety screening, request generation, structural QA, auto-repair, and packaging — in that order, automatically, resumably. Do not hand-roll any of these steps separately; they are already one connected pipeline.

1a. **Production gates run automatically — there is nothing to enable.** Every ordinary `generate_season()` call enforces the Duration Gate, the Islamic Authoring Gate, the Continuity Gate, and the final Season Acceptance Gate without any flag or parameter. A season is never marked `SEASON_COMPLETE` unless the Season Acceptance Gate explicitly reports `READY`. There is a test-only bypass (`DisableProductionGatesForTesting` in `tools/orchestration/testing_overrides.py`) — this prompt must never reference, suggest, or construct it. If gate enforcement is ever missing from a real production run, that is a defect to report, not a setting to look for.

1b. **When a gate blocks an episode** (status `GATE_REPAIR_REQUIRED`) **or blocks the season** (Season Acceptance Gate reports anything other than `READY`), the system does not automatically retry or rewrite the content — it stops and records the exact reason (which gate, which episode, why). Report this to whoever is operating the system rather than papering over it: a duration shortfall needs genuine additional story material (never padding — see item 9); an Islamic Gate failure needs either a real, eligible cited source or a rewrite that drops the specific unsourced attribution; a Continuity Gate failure (e.g. a Story State thread referenced before it was ever created) needs the actual story logic fixed. Corrected content must be registered again and the season call repeated with the same `season_id` to resume.

2. **Season planning and episode arcs**: the system produces one season concept with a real arc — episodes must build on each other, not read as disconnected premises. This comes from the authoring layer (`tools/authoring/`), not from this prompt re-describing story structure.

3. **Authoring**: real, original dialogue and action per episode — never templated or interchangeable filler. Reuse each character's established voice, personality, and relationships exactly as recorded in the Character Registry (`continuity/character_bible/`). Do not invent new characters outside the registry unless the season concept explicitly calls for one to be added to the registry first.

4. **Story State**: every episode's promises, unresolved threads, secrets, goals, running jokes, lessons, and callbacks must be read from and written back to Story State (`continuity/story_state/`) for the season. Do not reset continuity at episode boundaries. A promise made in episode 1 must still be knowable in episode 30.

5. **Continuity — character, environment, prop, camera**: every clip must be built through the existing Continuity system (Character/Environment/Prop/Camera Registries plus the Environment Continuity resolver), not re-described here. Characters must not drift in appearance, colour, markings, clothing, personality, relationships, voice, or established behaviour between clips or episodes. Locations and props must not change or vanish without the story explicitly calling for it.

6. **Scene-to-Clip Bridge**: convert authored scenes into ordered clips using the active provider's real capabilities — never assume a fixed clip length. Clip boundaries must fall on natural action/dialogue/camera boundaries, never mid-line. A camera change is itself a valid clip boundary.

7. **Clip-to-clip and episode-to-episode continuation**: every clip must inherit continuity state from the one before it (last-frame or video-extension continuation, environment carry-forward) exactly as the existing Last-Frame Continuity and Environment Continuity mechanisms already do. Do not describe or simulate this state manually.

8. **Duplicate-character prevention and reference images**: the system already selects and prioritizes reference images per clip within the active provider's real limits, and already seeds default duplicate-character negative constraints. Do not override this with manually written per-clip instructions.

9. **Duration is measured, not assumed.** The requested episode duration is enforced by the Duration Gate against the real planned clip count (clip count × the active provider's actual clip length), never against word count or a rough guess. If content comes back short, the fix is genuine additional story material — new scenes, new beats, deeper character moments. Never pad with repeated dialogue, artificial pauses, duplicated scenes, or an unneeded song just to hit a number. If content comes back long, tighten and cut deliberately rather than truncating wherever the episode happens to currently end.

10. **Songs and music**: do not force a song into every episode. A song belongs only where the story genuinely calls for one (a real emotional high point, a natural occasion). Where a song is used, keep its identity consistent if it recurs, and preserve character/scene/environment continuity immediately before and after it. This decision is recorded per-episode by the authoring layer (`song` field) — do not add music infrastructure beyond what already exists. Song lyrics are not exempt from the Islamic Authoring Gate (item 11) — a religious claim inside a lyric is checked exactly like one in dialogue. **`song.included: true` requires real, written `lyrics`** — a prose `lyrics_theme` describing what the song is about is not a song and will not satisfy the Song Gate. A scene that narrates characters singing without any actual verse/chorus text is not a completed song; write the real words.

11. **Islamic correctness — critical, fail-closed, non-negotiable**:
    - The authoring prompt itself is supplied only eligible source excerpts (`review_required=false`, not disputed) from the repository's real Islamic source files (`phase2/data/islamic/*.json`), each with its real citation ID, so there is real material to quote — do not improvise religious content the registry didn't supply.
    - The finished script (including every song's lyrics) is independently scanned afterward for religious-source claims. Any such claim must carry a citation to an eligible source; an uncited claim, a citation to a nonexistent ID, or a citation to a source still marked `review_required` all fail closed.
    - Never invent Qur'an quotations, hadith, Islamic rulings, religious facts, duas, Arabic wording, or religious interpretations. If a piece of religious content is needed and isn't already eligible in the source files, do not fabricate it — flag it as missing instead.
    - Never mark a `review_required` safety/citation item as resolved to let production continue. Per the repository's own explicit policy (`phase2/data/safety/review_resolutions.json`), such an item only clears when a real human reviewer's entry exists there — this is never auto-populated, and this prompt must not attempt to auto-populate it either.
    - Ordinary child-friendly expressions of kindness, gratitude, and everyday Islamic vocabulary (Alhamdulillah, Bismillah, Insha'Allah) are not claims and are not gated — do not over-block normal language.
    - Where the repository's policy requires fail-closed behaviour, fail closed. Report the specific blocking reason; do not guess, soften, or route around it.

12. **General safety**: every generated request is already screened against the repository's real content-restriction and scene-safety registries before anything is sent toward a provider. Do not weaken, duplicate, or second-guess this in prose — it already runs automatically and blocks unsafe content with a specific, named reason.

13. **Registry ID validation**: every character, environment, and prop ID referenced in authored content is already validated against the real Character/Environment/Prop Registries before any request is built. An unknown ID fails the whole clip closed with a named reason — it is never silently dropped or substituted. Do not reference a character, location, or prop that isn't already in the registries; if the story needs a new one, it must be added to the registry, not improvised in a prompt.

14. **Continuity across the whole season**: the Continuity Gate checks all episodes together, not one at a time — a Story State thread must exist before any episode references or resolves it, and every character/environment/prop ID must be valid everywhere in the season, not just within its own episode. This is what catches a later episode quietly referencing something that was never actually set up. Thread-ID validation runs against the real Story State system itself, not a separate re-implementation of it, so it can never silently drift out of sync with what the real system actually produces.

15. **QA and repair**: structural QA (reference-image coverage, continuation-anchor presence, environment-state freshness, unresolved safety reviews) runs automatically after each clip is planned. Auto-repair applies automatically for the specific, limited set of issues it's safe to fix (reprioritizing a dropped reference image, rebuilding against fresher continuity state), capped at a fixed number of attempts so a genuinely unresolvable issue surfaces for a human instead of looping forever.

16. **Packaging**: the finished season — or as much of it as could be completed given available credentials — is packaged as one ZIP containing the season roadmap, authored episode scripts, Story State, clip plans, the Character/Environment/Prop/Camera Registries as used, Clip State, generated request payloads, safety results, QA reports, gate results (Duration/Islamic/Song/Continuity/Season Acceptance), any generated video and assembled episodes, manifests, and a production status report. Use the existing season packager; do not hand-assemble this list. **If new environments/props are created for a season's story, their registry entries must be part of the package too** — a season referencing a location or object nobody outside the production run has ever seen is not a complete, reproducible package. Report the season's final `season_acceptance` status plainly, including its `note` field, which explicitly states that `READY` means pre-generation gates and real request-building passed — never describe a season as "complete" or "production-ready" from `READY` alone; that status does not mean video was rendered.

---

## HONEST LIMITS — DO NOT CLAIM OTHERWISE

- **Determinism applies to production instructions and continuity state, not to rendered pixels.** The system guarantees the *request* sent for each clip is consistent, safety-screened, and continuity-correct. It cannot guarantee an AI video model renders pixel-identical characters between clips — visual rendering remains probabilistic.
- **Real video generation requires a live Veo credential.** Without one, clips correctly stop at "waiting for external generation," not a fabricated success.
- **Real authoring at full scale requires a live authoring credential.** Without one, episodes correctly stop at "waiting for external authoring." A manual path exists (a written prompt file per episode/season, and a way to register the result) for producing real content without that credential.
- **Automated pixel-level Visual QA (character drift, duplicate characters visible in a render, prop/lighting/camera drift as actually rendered) requires a connected vision-capable backend that does not currently exist in this system.** Do not report a visual PASS unless a real vision backend actually analyzed real rendered output. Structural QA (everything checkable from data already on hand) is real and automatic; pixel-level QA is not, and must be stated as such every time, not just once.
- **Do not describe any of the above as solved** merely because the rest of the pipeline is real and automatic. Report status honestly: what ran, what's waiting on an external credential, and what remains unverified.

---

## OUTPUT EXPECTATIONS

The delivered package should read as one continuous, professionally planned season — not as disconnected AI-generated fragments. Intentional repetition (character identity, educational reinforcement, recurring jokes, a recurring song, safety phrasing, continuity notes) is correct and expected; mechanical, copy-pasted-feeling repetition across unrelated scenes is not. Creativity belongs in the authored story; determinism belongs in the production state, validation, and rendering instructions that carry that story through to clips.
