# Islamic Kids Studio — AI Content Operating System

Repository version: **v2.72** — see `CHANGELOG.md` for the full fix history.

## What this is
A repository-driven pipeline for generating complete Islamic children's
YouTube episode packages (story, script, image/animation prompts, thumbnail,
SEO metadata, subtitles, QA checklist) from a single topic input.

## Quick start (for a coding agent — Claude Code, Cursor, etc.)
1. Open this repository in your agent.
2. Point it at **`MASTER_PROMPT.md`** — this is the only prompt you need to
   give it directly.
3. Send: `Topic: <your next video idea>`
4. The agent follows the 20 automatic steps in `MASTER_PROMPT.md`, writes
   the 27 output files into `output_package/<episode_slug>/`, then runs:
   ```
   python3 tools/package_episode.py <episode_slug>
   ```
   to produce `output_package/<episode_slug>.zip` — a single downloadable
   file containing the full production package for that episode.

## Before you publish this repo
Run the validator. It actually checks the repo instead of asserting it's
clean:
```
python3 tools/validate_repo.py .
```
It checks JSON/YAML validity, that every file the repo references actually
exists, and that no old/legacy character names have crept back in. Fix any
line under `ERRORS` before treating the repo as production-ready. Lines
under `WARNINGS` need a human read (some are expected — e.g. the historical
audit reports below, which describe *past* broken states on purpose).

## Repository map
- `MASTER_PROMPT.md` — the single entry-point prompt. Start here.
- `DESIGN_PRINCIPLES.md` — the Constitution: non-negotiable rules every
  output must satisfy.
- `AUTHORITY_HIERARCHY.md` — conflict-resolution order when two files
  disagree. `phase1/docs/governance/` has the operational detail on top
  of this: `authority_rules.md` (which file owns which fact),
  `conflict_resolution.md`, `review_workflow.md`, `deprecation_policy.md`,
  `versioning_policy.md`, `change_log_policy.md`.
- `phase1/docs/decisions/adr/` — Architectural Decision Records for the
  big structural choices (character system, visual style, curriculum
  order, prompt strategy). Read these before changing any of them.
- `phase1/docs/` — brand, story, character, curriculum, Islamic, language,
  and SEO rules (human-readable). `phase1/docs/curriculum/CHILD_DEVELOPMENT_MATRIX.md`
  breaks "ages 2-8" into three concrete age bands.
- `phase2/data/` — config, databases, Islamic reference data, pronunciation
  dictionaries, SEO keyword data. `phase2/data/database/world_state.json` is the
  long-term continuity memory (separate from `current_state.json`, which
  only tracks what's active right now).
- `phase3/knowledge/` — structured knowledge base (characters, world,
  curriculum, story, education, language) used for AI retrieval.
  `failures/` documents specific anti-patterns to avoid, grounded in real
  findings from repository review. `concepts/` holds Islamic Concept
  Database packages (one retrievable unit per concept — Quran, hadith,
  dua, prophet, vocabulary, and conflict all cross-linked).
  `phase3/knowledge/vocabulary/islamic_vocabulary.json` teaches word meanings (distinct
  from `pronunciation_dictionary.json`, which only covers pronunciation).
  `story/` holds `conflict_library.json`, `story_patterns.json`,
  `curiosity_hooks.json`, `ending_styles.json`, and
  `emotion_database.json` — reusable building blocks that keep episodes
  varied instead of formulaic.
- `phase4/engine/` — the generation prompts, templates, and checklists.
  `phase4/engine/quality/rubric.md` is the 10-dimension scored quality bar
  with a hard auto-reject gate, on top of the binary PASS/FAIL checks in
  `qa_checklist.md`. `phase4/engine/teaching/teaching_strategy.json` maps concept+age to
  teaching method. `phase4/engine/prompts/shorts_prompt.md` is the real Shorts/Reels
  spec.
- `phase5/orchestration/` — pipeline, workflow, and QA orchestration
  docs. `phase5/orchestration/planning/topic_planner.md` answers "what to make next";
  `phase5/orchestration/planning/knowledge_builder_pipeline.md` is the repeatable process for
  turning a source book into structured data.
- `phase1/docs/community/` — `MODERATION.md`, `PARENT_TRUST_PAGE.md`,
  `SPONSORSHIP_POLICY.md`. `phase1/docs/governance/dispute_response.md`
  covers what happens when a published episode gets a real theological
  challenge.
- `sources/characters/` — the **locked, canonical** visual character
  system (Zayd, Amira, Dada Yusuf, Baba Ahmad, Ummi Layla, Nuri). Copy the
  `LOCKED DESCRIPTION BLOCK` word-for-word into every image/animation
  prompt involving these characters — never paraphrase it.
- `assets/characters/` — real turnaround reference images for all six
  characters. `assets/brand/logo.png` — channel logo.
- `phase1/docs/seo/COMPETITOR_STRATEGY.md` — how to format episodes so
  YouTube's recommendation system treats them as a close match to a target
  competitor channel. Populate `phase2/data/database/competitor_benchmark.json`
  with real data before relying on it.
- `MULTI_CHANNEL.md` — what's reusable vs. what to fork when starting a
  second Islamic channel.
- `sources/islamic_books/CATALOG.md` — tracks all uploaded reference
  books, what's been extracted into `phase2/data/islamic/` so far, and a
  licensing flag on the Quran translation files (don't extract wording
  from those — see the file for why).
- `roadmap/` — `planned_features.md`, `backlog.md`, `completed.md`.
- `tools/` — `validate_repo.py` (link/schema/duplicate-ID/version checker
  — also writes `REPO_HEALTH_REPORT.md`), `package_episode.py` (zips a
  finished episode for download), `prompt_regression_test.py`
  (capture/compare harness for catching quality drops after prompt edits
  — see its header for what still requires a live model call).
- `CHANGELOG.md` — version history. Every entry states how it was
  verified (`change_log_policy.md`), not just what changed.
- `AUDIT_REPORT.md` / `FINAL_AUDIT_REPORT.md` — historical audit logs,
  explicitly marked superseded. Don't treat their scores as current status.

## Cast reference
| Character | Role | Locked description | Reference image |
|---|---|---|---|
| Zayd | Lead boy, age 5 | `sources/characters/characters/zayd.md` | `assets/characters/zayd_turnaround.jpeg` |
| Amira | Lead girl, age 5 | `sources/characters/characters/amira.md` | `assets/characters/amira_turnaround.jpeg` |
| Dada Yusuf | Grandfather | `sources/characters/characters/dada_yusuf.md` | `assets/characters/dada_yusuf_turnaround.jpeg` |
| Baba Ahmad | Father | `sources/characters/characters/baba_ahmad.md` | `assets/characters/baba_ahmad_turnaround.jpeg` |
| Ummi Layla | Mother | `sources/characters/characters/ummi_layla.md` | `assets/characters/ummi_layla_turnaround.jpeg` |
| Nuri | Mascot (lamb) | `sources/characters/characters/nuri.md` | `assets/characters/nuri_turnaround.jpeg` |

## What happens after the zip
This repository generates **prompts and production documents**, not
rendered video. `image_prompts.md`, `thumbnail.md`, `animation_directions.md`,
and `music_notes.md` from the output package are what you feed into your
image/animation generation tool (Midjourney, Kling, Runway, etc.) — that
step happens outside this repo, using the locked character description
blocks so every episode's characters stay visually consistent.

## See it actually work
`examples/` has three real, complete example runs — one per execution
mode (Production, Assisted, Blocked — see
`phase5/orchestration/planning/execution_modes.md`, added v2.14). Not
descriptions of what the pipeline would do — actual runs of it. Read
`examples/README.md` first.

## v2.72 Current Operator Paths

- Current documentation: `docs/current/`
- Historical release evidence: `archive/`
- Active roadmap: `production/roadmaps/active_roadmap.json`
- One-command validation: `python tools/validate_release.py`
- Local-only bootstrap: `MASTER_PROMPT.md` is intentionally excluded from distributions.
