# Islamic Kids Studio — Complete Project Guide

**Repository version: v2.12** · Brand: Islamic Kids Studio · Handle: @IslamicKidsHQ
**Last updated:** 2026-08-03

This is the full reference document for the repository. It has two main
parts — **Part A** is written for someone with no coding background who
just wants to understand what this is and how to use it. **Part B** is
the technical reference — full file structure, what every folder does,
and how to modify or extend the system. Part C covers suggestions,
scaling, and what's still open.

If you only read one section, read **Part A, Section 1** (what this is)
and **Part B, Section 2** (the file map) — those two answer almost every
question that comes up later.

---

# PART A — For Non-Technical Readers

## A1. What this actually is, in plain terms

This is a **content-generation system** for a children's Islamic YouTube
channel. It is not an app, not a website, not a video editor. It's a
large, organized folder of instructions, rules, and reference data that
an AI coding assistant (like Claude Code, Cursor, or similar tools)
reads and follows to turn one sentence — a topic — into a complete
package of everything needed to produce one episode.

Think of it like a very detailed recipe book plus a pantry of verified
ingredients, for someone else (an AI) to cook from. You say "make me an
episode about kindness," and the AI:

1. Looks up what "kindness" means in the repository's own data (real
   Quran verses, real hadith, real duas — not made up).
2. Picks the right characters (always the same six: Zayd, Amira, Dada
   Yusuf, Baba Ahmad, Ummi Layla, and Nuri the lamb) so they look and
   act consistently in every episode.
3. Writes a story following a fixed structure (opening → problem →
   response → resolution → closing) so every episode has a similar
   comforting shape for young viewers.
4. Writes out everything needed to actually produce the video: the
   script, image descriptions for an AI image generator, camera
   directions, a song, subtitles (English and Arabic), a YouTube title,
   description, tags, and a thumbnail description.
5. Packages it all into one downloadable zip file.

You then take that zip and its text files into whatever tool you
actually use to generate images/animation (Gemini, Meta AI, etc.) and
audio (your own software), and assemble the finished video yourself.
**This repository does not create video, audio, or images itself** — it
creates the complete, detailed instructions for making them.

## A2. Why it's built this way (not just "ask an AI to write a story")

If you just asked an AI "write me an Islamic kids story," you'd get
inconsistent characters, made-up religious quotes, repetitive plots, and
no SEO/production materials. This repository exists to prevent all of
that by keeping:

- **A fixed cast** with locked visual descriptions, so Zayd looks like
  Zayd in every single episode.
- **A real, sourced Islamic reference library** — every dua, Quran verse,
  and hadith cited in an episode traces back to a named real source
  (specific books, specific pages), never invented.
- **A quality checklist** every episode is scored against before it's
  considered ready.
- **A "who checks what" system** that doesn't assume you personally have
  Islamic religious training (see Section A4) — you check whether things
  are properly sourced; an actual qualified person checks whether the
  religious content is accurate.

## A3. How you'd actually use it, step by step

1. Give the whole repository (as a zip, or connected to a coding
   assistant) to your AI tool of choice.
2. Tell it: `Topic: <your idea>` — for example,
   `Topic: Being kind to a new friend at school`.
3. The AI works through the repository's master instruction file and
   produces a folder of ~28 text files (script, prompts, subtitles,
   SEO info, etc.) plus a **Verification Report** and a **Quality
   Score**.
4. It zips that folder for you.
5. **You check the Verification Report** — this just tells you whether
   every religious claim in the episode has a real, named source. You
   don't need any Islamic background to read it; it's a checklist, not
   a judgment call. See Section A4.
6. You take the image/animation/camera-direction text into your
   image/video generation tool, and the lyrics text into your audio
   tool, and assemble the video.
7. Before actually publishing, get a real qualified reviewer (imam,
   scholar, or similarly qualified person) to check the specific
   religious content cited — this repository tracks whether that's
   happened, but can't do it for you.

## A4. "Who checks what" — this matters, read this part

Because you (as the creator) may not have formal Islamic religious
training, the system is deliberately split into two separate kinds of
checking so you're never asked to make a call you're not equipped to
make:

| Check | Who does it | What it actually involves |
|---|---|---|
| **Is every claim sourced?** | **You** | Read the `verification_report.md` file in each episode's output. It lists every religious claim and whether it has a named source. No religious knowledge needed — it's a "is this box checked or not" read. |
| **Is the source authentic and correctly applied?** | **An external qualified person** (imam, scholar, or similar) | This does require real Islamic knowledge, so the system never asks you to do it. The repository just tracks, per piece of content, whether this step has happened yet (it currently hasn't, for anything — see Section C). |

An episode is only truly ready to publish once **both** checks are done.

## A5. Quick glossary (plain language)

- **Episode package** — the folder/zip of ~28 files produced for one
  topic; everything needed to build one video.
- **Locked character** — a character whose appearance is written down
  word-for-word and must be copied exactly every time, so they don't
  visually drift between episodes.
- **Verification Report** — the citation checklist described in A4.
- **Quality Score** — a 0–10 score across 10 categories (is it accurate,
  age-appropriate, well-paced, etc.) generated for every episode.
- **Review Queue** — a tracking file listing every episode/content batch
  and whether it's still a draft, been checked, been approved, or is
  live.

---

# PART B — Technical Reference

## B1. How the system works, mechanically

There is **no running code, server, or app** in the normal sense. This
is a structured set of Markdown (`.md`) instruction/rule files and JSON
(`.json`) data files, plus a handful of real Python scripts in `tools/`.
An AI coding agent (something with file-reading and reasoning ability,
e.g. Claude Code) is the "engine" — it reads `MASTER_PROMPT.md`, follows
its 28 numbered steps, reads whichever data files each step calls for,
and writes output files. The Python scripts handle the purely mechanical
parts (validating file integrity, zipping a finished package) that don't
need an LLM.

**Entry point:** `MASTER_PROMPT.md` (repository root). Everything else is
either referenced by it directly, or referenced by something it
references (via `knowledge_index.json`, a lookup table from concept
names to file paths).

## B2. Full folder map

```
/ (repository root)
├── MASTER_PROMPT.md          ← THE entry point. Give this to the AI agent.
├── DESIGN_PRINCIPLES.md      ← Non-negotiable rules (the "Constitution")
├── AUTHORITY_HIERARCHY.md    ← Which file wins when two disagree
├── VERSION_COMPATIBILITY.md  ← Single source of truth for repo version
├── CHANGELOG.md              ← Full history of every change, ever
├── README.md                 ← Short quick-start (this file is the long version)
├── MULTI_CHANNEL.md          ← How to reuse this for a second channel
├── repository_manifest.json  ← Machine-readable repo metadata
├── knowledge_index.json      ← Concept → file-path lookup table (critical file)
├── REPO_HEALTH_REPORT.md     ← Auto-generated by the validator, current status
│
├── phase1/docs/              ← Human-readable rules & brand documentation
│   ├── master/                 MASTER.md, README.md — overview docs
│   ├── brand/BRAND.md           Colors, logo, handle, watermark
│   ├── story/STORY.md           The fixed 5-beat episode structure
│   ├── character/CHARACTER.md   Character design rules
│   ├── curriculum/              CURRICULUM.md + CHILD_DEVELOPMENT_MATRIX.md
│   ├── islamic/ISLAMIC.md       Islamic content rules
│   ├── language/LANGUAGE.md     Language/pronunciation rules
│   ├── seo/                     SEO.md + COMPETITOR_STRATEGY.md
│   ├── voice/VOICE.md           Voice acting direction rules
│   ├── animation/ANIMATION.md   Animation style rules
│   ├── rules/RULES.md           Universal content rules
│   ├── content/CONTENT_STRATEGY.md
│   ├── workflows/WORKFLOW.md
│   ├── templates/TEMPLATE.md
│   ├── prompts/PROMPT.md
│   ├── memory/MEMORY.md
│   ├── roadmap/ROADMAP.md       Points to /roadmap/ (see below)
│   ├── decisions/               DECISION.md + adr/ (Architectural Decision Records)
│   ├── governance/              See B4 — the rulebook for how the repo governs itself
│   └── community/               Moderation, parent trust page, sponsorship policy
│
├── phase2/data/               ← Structured data (the actual facts/settings)
│   ├── config/                 settings.yaml, languages.yaml, retrieval_ranking_weights.yaml
│   ├── islamic/                 8 files: duas, hadith, quran_verses, prophets,
│   │                            good_manners, daily_sunnah, festivals, companions
│   │                            (37 total entries — see B5 for counts)
│   ├── language/                pronunciation_dictionary.json, arabic_words.json, islamic_names.json
│   ├── seo/                     keyword_database.csv
│   └── database/                Production state: current_state.json, world_state.json,
│                                 available_topics.json, topic_graph.json,
│                                 completed_topics.json, future_topics.json,
│                                 published_videos.json, review_queue.json,
│                                 character_versions.json, active_characters.json,
│                                 character_relationships.json, asset_registry.json,
│                                 hijri_calendar_schedule.json, creator_edits_log.json,
│                                 competitor_benchmark.json (template, not yet filled)
│
├── phase3/knowledge/          ← AI-retrievable structured knowledge
│   ├── characters/              knowledge_characters.json (personality/relationships)
│   ├── concepts/                20 Islamic Concept packages (see B5)
│   ├── vocabulary/              islamic_vocabulary.json (50 words)
│   ├── curriculum/              knowledge_curriculum.json + dependency graph
│   ├── world/                   knowledge_world.json (environments)
│   ├── story/                   knowledge_story.json, conflict_library.json (30),
│   │                            story_patterns.json (5), curiosity_hooks.json (6),
│   │                            ending_styles.json (5), emotion_database.json (6)
│   ├── education/               General education knowledge
│   ├── language/                Language knowledge
│   └── failures/                4 documented anti-patterns to avoid
│
├── phase4/engine/             ← The actual generation prompts
│   ├── prompts/                 14 prompt modules (story, script, dialogue, image,
│   │                            animation, thumbnail, music, voice, subtitle, seo,
│   │                            metadata, qa, review, shorts)
│   ├── templates/               episode_template.md, story_template.md, scene_template.md
│   ├── writing/dialogue_rules.md
│   ├── metadata/episode_metadata_template.md
│   ├── thumbnails/thumbnail_template.md
│   ├── checklists/qa_checklist.md
│   ├── quality/rubric.md        10-dimension quality scoring + auto-reject gate
│   ├── teaching/teaching_strategy.json  Concept+age → teaching method
│   └── cinematography/camera_language.json  6 structured shot/lighting/camera setups
│
├── phase5/orchestration/      ← Pipeline coordination
│   ├── workflows/generation_workflow.md
│   ├── quality/quality_workflow.md
│   ├── errors/error_recovery.md
│   ├── memory/ (session memory rules)
│   └── planning/                topic_planner.md, retrieval_ranking.md,
│                                 knowledge_builder_pipeline.md
│
├── sources/                   ← Original/reference source material
│   ├── characters/              character_index.json + characters/*.md (6 locked
│   │                            character description files — the visual "bible")
│   │                            + GUEST_CHARACTERS.md
│   ├── islamic_books/           CATALOG.md — tracks the 27 reference books provided
│   ├── education/, business/, market/, psychology/, youtube/, islamic/
│
├── assets/                    ← Real image files
│   ├── characters/              6 real turnaround reference JPEGs
│   └── brand/logo.png
│
├── tools/                     ← The only actual executable code
│   ├── validate_repo.py         Checks the whole repo for errors — RUN THIS OFTEN
│   ├── package_episode.py       Zips a finished episode folder
│   └── prompt_regression_test.py  Compares output before/after a prompt edit
│
├── examples/                  ← A real, complete proof episode (see B6)
├── output_package/            ← Where new episodes get written before zipping
├── roadmap/                   ← completed.md, planned_features.md, backlog.md
├── tests/fixtures/            ← Used by prompt_regression_test.py
├── psychology/, research/     ← Supporting research notes
└── (root files) AUDIT_REPORT.md, FINAL_AUDIT_REPORT.md — historical audit
    logs, explicitly marked superseded, kept for history only
```

## B3. The single most important file: `knowledge_index.json`

Nothing in this repository is meant to be "loaded all at once." Instead,
`knowledge_index.json` is a lookup table: it maps a concept name (like
`"islamic"`, `"characters"`, `"story"`, `"governance"`) to the exact list
of file paths relevant to that concept. `MASTER_PROMPT.md` reads this
index first, then only loads the specific files it actually needs for
the current episode — this keeps things fast and avoids irrelevant or
contradictory content leaking into generation.

**If you add a new file, you must add it to `knowledge_index.json`** —
under the right concept category — or the pipeline will never find it.

## B4. The governance layer — how the repo keeps itself honest

`phase1/docs/governance/` is the rulebook for how the repository governs
its own content and changes:

- **`authority_rules.md`** — for every kind of fact, states which single
  file is the source of truth (so the same fact is never defined
  differently in two places).
- **`conflict_resolution.md`** — what to do when two files disagree.
- **`review_workflow.md`** + **`verification_pipeline.md`** — the
  citation/scholar-review split described in Part A, Section A4, in full
  technical detail. Every Islamic-content entry carries three fields:
  `citation_verified`, `source_verified`, `scholarly_reviewed` (see B5).
- **`execution_modes.md`** (added v2.14) — replaces the old binary
  PASS/BLOCK behavior with three outcomes (Production, Assisted,
  Blocked) plus Smart Fallback, Auto Duration Correction, and Draft
  Curriculum Mode. See `examples/README.md` for one real generated
  episode per mode.
- **`deprecation_policy.md`** — how to retire or correct old content
  without breaking episodes that already used it.
- **`versioning_policy.md`** — one version number for the whole repo,
  tracked in `VERSION_COMPATIBILITY.md`; per-file `version: 1.1`
  frontmatter labels are separate, static authoring labels, not synced
  to the repo version (this distinction matters — see `CHANGELOG.md`
  v2.12 for why).
- **`change_log_policy.md`** — every `CHANGELOG.md` entry must be
  independently verifiable, not just asserted.
- **`dispute_response.md`** — procedure if a published episode's
  religious content is publicly challenged.
- **The earlier per-episode review pipeline was superseded in v2.10** by
  `verification_pipeline.md` — the earlier version wrongly implied the
  creator judges Islamic accuracy; the current version correctly splits
  that from the creator-doable citation check.
- **Architectural Decision Records** (`phase1/docs/decisions/adr/`) — 4
  files documenting *why* the big structural choices were made (the
  character system, the visual-style strategy, the curriculum ordering,
  the single-master-prompt strategy). Read these before changing any of
  those four things.

## B5. Current data volume (as of v2.12 — check `REPO_HEALTH_REPORT.md` for live numbers)

| Data type | File(s) | Count |
|---|---|---|
| Duas | `phase2/data/islamic/duas.json` | 6 |
| Hadith | `phase2/data/islamic/hadith.json` | 4 |
| Quran verses | `phase2/data/islamic/quran_verses.json` | 5 |
| Prophets | `phase2/data/islamic/prophets.json` | 4 |
| Good manners | `phase2/data/islamic/good_manners.json` | 8 |
| Daily sunnah | `phase2/data/islamic/daily_sunnah.json` | 5 |
| Festivals | `phase2/data/islamic/festivals.json` | 3 |
| Companions | `phase2/data/islamic/companions.json` | 2 |
| **Islamic references, total** | | **37** |
| Vocabulary words | `islamic_vocabulary.json` | 50 |
| Concept packages | `phase3/knowledge/concepts/*.json` | 20 |
| Story conflicts | `conflict_library.json` | 30 |
| Story patterns | `story_patterns.json` | 5 (deliberately capped — see reasoning in `CHANGELOG.md` v2.9) |
| Curiosity hooks | `curiosity_hooks.json` | 6 |
| Ending styles | `ending_styles.json` | 5 |
| Emotion mappings | `emotion_database.json` | 6 |
| Characters (locked cast) | `sources/characters/characters/` | 6 (Zayd, Amira, Dada Yusuf, Baba Ahmad, Ummi Layla, Nuri) |
| **Citation/review status (107 Islamic+vocab+concept entries)** | | 21 have a real named source (`citation_verified: true`); 0 have been checked by a qualified scholar (`scholarly_reviewed: true`) |

## B6. The proof episode — read this before building your first real one

`examples/ep_tawakkul_lost_toy/` is a **real, complete 28-file output**
produced by actually running the full pipeline once — not a description
of what it would produce. `examples/README.md` explains it in detail.
Key thing to know: its own Quality Score correctly failed the auto-reject
gate (Islamic-accuracy dimension scored 6, below the required 7)
*because* its sources aren't scholar-reviewed yet — that's the system
working correctly, not a bug. Use this folder as the reference for
exactly what a complete, correctly-formatted episode package looks like.

## B7. How to actually run things

```bash
# Validate the whole repository (do this after any change)
python3 tools/validate_repo.py .
# → writes REPO_HEALTH_REPORT.md, exits non-zero on real errors

# Package a finished episode folder into a downloadable zip
python3 tools/package_episode.py <episode_slug>
# expects output_package/<episode_slug>/ to already contain the
# generated files; warns loudly if review_queue.json doesn't show
# "approved" status for that episode

# Compare output before/after editing a prompt (regression check)
python3 tools/prompt_regression_test.py capture <topic_slug>   # before editing
python3 tools/prompt_regression_test.py compare <topic_slug>   # after regenerating
```

## B8. How to modify things (common tasks)

**Add a new Islamic reference (dua/hadith/verse/etc.):**
Follow `phase5/orchestration/planning/knowledge_builder_pipeline.md` —
name a real source, set `citation_verified`/`source_verified` honestly
based on whether you actually checked it, always set
`scholarly_reviewed: false` until an actual qualified reviewer confirms
it. Add the entry to the right file in `phase2/data/islamic/`.

**Add a new topic:**
Add to `phase2/data/database/available_topics.json` with correct
`prerequisites` (check `topic_graph.json` for the dependency chain logic
in `ADR_003_curriculum_order.md`), and to `topic_graph.json`'s
nodes/edges.

**Add a new character:**
Read `ADR_001_character_system.md` and `ADR_002_visual_style.md` first.
New characters need a locked description block in
`sources/characters/characters/`, real reference art in
`assets/characters/`, and entries in `knowledge_characters.json` and the
`phase2/data/database/` character files — **never create a second,
parallel character system** (this happened once, see `ADR_001` for what
went wrong).

**Change the version number:**
Update `VERSION_COMPATIBILITY.md` first, then
`repository_manifest.json`, `knowledge_index.json`,
`phase2/data/config/settings.yaml`, `MASTER_PROMPT.md`'s header, and
`DESIGN_PRINCIPLES.md`'s header — then run `tools/validate_repo.py` to
confirm they all match.

**Start a second channel:**
Read `MULTI_CHANNEL.md` — it lists exactly what's reusable as-is
(governance, tooling, child-development data, Islamic reference data)
versus what must be forked fresh (brand, characters, world, production
state).

---

# PART C — Suggestions, Scaling, and Open Items

## C1. What genuinely still needs doing (highest priority first)

1. **Get a real scholar/qualified reviewer** to check the 21 entries
   that already have `citation_verified: true` (see B5) — this is the
   cheapest, highest-leverage next step. The other 86 entries need a
   real source found first (a creator-doable task — no religious
   training needed, just research) before a scholar's time is worth
   spending on them.
2. **Populate `competitor_benchmark.json`** with real data from whichever
   channel you're benchmarking against — `COMPETITOR_STRATEGY.md`'s
   guidance can't do anything useful until this has real numbers in it.
3. **Produce a second and third real episode** beyond the one proof
   episode, to confirm the pipeline works consistently, not just once.

## C2. Medium-term scaling ideas

- **Knowledge base growth**: current volume (37 Islamic references, 50
  vocab words, 30 conflicts) is enough for roughly 15-20 episodes before
  content starts repeating (see `phase3/knowledge/failures/repeated_story.md`).
  Grow this in batches tied to actual production, not one giant seed —
  each new batch should go through the same citation/review tracking as
  everything else (`review_queue.json`).
- **Multi-language expansion**: Arabic subtitle support is real and
  active as of v2.9; Urdu and other languages are scaffolded in
  `languages.yaml` but marked `planned`, not built out yet.
- **Analytics feedback loop**: `phase2/data/database/creator_edits_log.json`
  exists as a dormant scaffold — intentionally not wired into generation
  yet, because there isn't enough published-episode data to learn from
  reliably (needs ~20-30 real episodes' worth of edits first, per its
  own stated activation criteria).

## C3. Guardrails worth keeping in mind as this grows

- **Don't build a second parallel system for anything that already has
  one** — this repository's single worst historical bug (see `ADR_001`)
  was exactly that (two incompatible character casts existing at once).
  The `authority_rules.md` table exists specifically to prevent this
  happening again for any other kind of data.
- **Don't skip the citation-completeness check even for "obviously
  fine" content** — the `verification_report.md`/Evidence Summary
  workflow exists because it's cheap to run and catches real gaps (see
  the proof episode in `examples/`, where it correctly caught two
  real, unreviewed-but-real citations).
- **Re-run `tools/validate_repo.py` after any batch of changes** — it
  has caught real, otherwise-invisible bugs multiple times in this
  repository's history (a two-character-system conflict, 18 stale
  hardcoded version references, several broken file paths). It's cheap
  to run and has a track record of finding real problems.

## C4. Suggested cadence going forward

- **Before every new episode batch:** check `topic_planner.md`'s
  suggestions against `completed_topics.json`, rather than picking
  topics ad hoc.
- **Every few episodes:** run `tools/validate_repo.py`, skim
  `REPO_HEALTH_REPORT.md`.
- **Periodically:** hand this whole repository to a fresh AI session
  with an audit prompt (a working one exists earlier in this
  conversation's history) — independent audits have caught real issues
  twice already in this project's history, and cost almost nothing to
  run.

---

*This document is a snapshot of the repository at v2.12 (2026-08-03).
For the live, authoritative state, always defer to `VERSION_COMPATIBILITY.md`,
`CHANGELOG.md`, and `REPO_HEALTH_REPORT.md` over this file if they ever
disagree — this guide should be regenerated after major version bumps,
but treat it as a map, not the territory.*
