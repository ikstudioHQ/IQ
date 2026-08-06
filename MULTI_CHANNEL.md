---
id: GOVERNANCE_MULTI_CHANNEL_ARCHITECTURE
version: 1.0
status: production
depends_on: [authority_rules.md, phase1/docs/brand/BRAND.md]
used_by: [Human Maintainers]
last_updated: 2026-07-31
---

# MULTI_CHANNEL.md — Reusing This Repository For a New Channel

The creator plans more Islamic YouTube channels beyond Islamic Kids
Studio. This file defines what's reusable as-is, what needs forking, and
what needs a small adapter — so that starting channel #2 is an afternoon
of config changes, not a repeat of this entire repository build.

## The split: reusable core vs. brand-specific layer

**Reusable across any Islamic channel, unchanged (the "core"):**
- `phase2/data/islamic/*.json` — duas, hadith, Quran verses, prophets,
  good manners, daily sunnah, festivals, companions. This is Islamic
  reference data, not brand content. A new channel targeting a different
  age group or format still draws from the same underlying facts.
- `sources/islamic_books/CATALOG.md` and the extraction principle in it.
- `phase1/docs/curriculum/CHILD_DEVELOPMENT_MATRIX.md` — child
  development facts aren't brand-specific.
- `phase1/docs/governance/` — the governance layer (authority rules,
  conflict resolution, review workflow, versioning, deprecation, changelog
  policy) is a process framework, not brand content.
- `tools/` — `validate_repo.py`, `package_episode.py`,
  `prompt_regression_test.py` are all brand-agnostic tooling.
- `phase4/engine/quality/rubric.md` — the 10 dimensions apply to any
  Islamic children's content; only the specific age-band numbers would
  need light adjustment if a new channel targets a different age range.

**Must fork/replace per channel (the "brand-specific layer"):**
- `phase1/docs/brand/BRAND.md` — name, handle, logo, colors, watermark.
- `sources/characters/` — a new channel needs its own original
  characters (never reuse Zayd/Amira's design for a different channel —
  see `ADR_002_visual_style.md`; a new cast needs its own locked
  description blocks and turnaround art).
- `assets/characters/`, `assets/brand/` — new channel's own art.
- `phase3/knowledge/characters/knowledge_characters.json`,
  `phase2/data/database/active_characters.json`,
  `character_versions.json`, `character_relationships.json` — rebuilt
  for the new cast, following the same schema (this is exactly the
  schema `ADR_001_character_system.md` established — reuse the
  *pattern*, not the *content*).
- `phase3/knowledge/world/knowledge_world.json`,
  `phase3/knowledge/story/knowledge_story.json` — new environments/story
  universe if the new channel has a different setting.
- `phase2/data/database/current_state.json`, `last_episode.json`,
  `world_state.json`, `available_topics.json`, `topic_graph.json`,
  `completed_topics.json`, `published_videos.json` — each channel's own
  production state; never shared between channels.
- `phase1/docs/seo/COMPETITOR_STRATEGY.md` +
  `competitor_benchmark.json` — each channel likely targets a different
  competitor/niche.
- `MASTER_PROMPT.md`'s worked example (references Zayd/Amira/env_home) —
  update the example to the new cast so a coding agent isn't confused by
  a stale example from a different channel.

**Depends on the new channel's decisions (case by case):**
- `phase1/docs/curriculum/CURRICULUM.md` /
  `phase3/knowledge/curriculum/knowledge_curriculum.json` — if the new
  channel targets the same 2-8 age range with similar values-based
  content, the curriculum *structure* and *ordering logic*
  (`ADR_003_curriculum_order.md`) can be reused directly, with topic
  selection adjusted. If it targets a different age range or focus
  (e.g. teens, or Quran memorization specifically), the structure needs
  real rework, not just a copy.

## Recommended folder pattern for multiple channels
When channel #2 is started, structure it as a sibling repository (or a
top-level folder in a monorepo) that:
1. Copies `tools/`, `phase1/docs/governance/`,
   `phase1/docs/curriculum/CHILD_DEVELOPMENT_MATRIX.md`,
   `phase4/engine/quality/rubric.md` unchanged.
2. **References** (doesn't copy) `phase2/data/islamic/*.json` from this
   repository as a shared data source, if practical for the chosen
   tooling — or copies it once and tracks it as a shared upstream so
   fixes/expansions to Islamic reference data benefit both channels
   without manual re-syncing. Document whichever choice is made in that
   channel's own `authority_rules.md`.
3. Forks `BRAND.md`, `sources/characters/`, `assets/`, and all
   `phase2/data/database/*` production-state files fresh.
4. Writes its own `MASTER_PROMPT.md` worked example using its own cast.
5. Runs `tools/validate_repo.py` before first use, same as this repo.

## What this explicitly avoids
Do not try to make one `MASTER_PROMPT.md` serve multiple channels via a
"channel_id" switch inside the same repository. That reintroduces the
exact class of bug `ADR_001_character_system.md` documents (two
character systems coexisting, ambiguous which applies) — just for
"channel" instead of "cast." Separate repositories/folders per channel,
sharing only the genuinely brand-agnostic core listed above, is the
safer pattern.

## Related Files
`phase1/docs/governance/authority_rules.md`,
`phase1/docs/decisions/adr/ADR_001_character_system.md`,
`phase1/docs/decisions/adr/ADR_002_visual_style.md`
