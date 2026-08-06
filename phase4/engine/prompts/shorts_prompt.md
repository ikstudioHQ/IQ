---
id: PROMPTS_SHORTS
version: 1.0
status: production
depends_on: [phase1/docs/story/STORY.md, phase3/knowledge/story/curiosity_hooks.json]
used_by: [AI Pipeline, Content Generator]
last_updated: 2026-08-01
---

# shorts_prompt.md — Shorts / Reels Profile

## Purpose
Produces a standalone 30-45 second vertical (9:16) video package — either
a cutdown of a full episode's single strongest beat, or a purpose-built
short for a topic that doesn't need a full episode.

## Two modes

**Mode A — Cutdown (from an existing episode):**
1. Read the source episode's `scene_breakdown.md`.
2. Identify the single scene with the highest emotional peak — the
   conflict's turning point or the resolution moment, never the opening
   or closing beat alone (those don't work as a 30-45 second standalone).
3. Build a self-contained short around that one scene: a 3-5 second hook
   (from `curiosity_hooks.json`, re-cut to fit, not the source episode's
   original opening), the peak moment itself, and a 3-5 second resolution
   or call-to-subscribe.

**Mode B — Purpose-built (from a topic directly):**
1. Same structure, but written fresh for the 30-45 second runtime — one
   single beat only, no 5-beat structure. Pick a single conflict from
   `conflict_library.json` and resolve it in one breath.

## Structure (both modes)
- **0-3 sec: Hook.** Must land the emotional premise instantly — no
  scene-setting, no "let's learn about." Use `curiosity_hooks.json`.
- **3-30 sec: The moment.** One clear beat, one clear emotion (see
  `emotion_database.json` for the voice/camera/pace mapping for whichever
  emotion the beat centers on).
- **30-40 sec: Resolution + one-line takeaway.** Stated, not lectured —
  a single sentence, per `DESIGN_PRINCIPLES.md`'s "show don't tell" rule
  applied at short-form speed.
- **40-45 sec: Soft CTA.** "Follow for more" styled to match brand voice,
  never generic/pushy.

## Required outputs (reduced set vs. full Episode profile)
```
output_package/<slug>_short/
  short_script.md
  short_scene.md          (single scene, not a full breakdown)
  image_prompts.md        (self-contained blocks, same rule as full episode)
  animation_directions.md (self-contained blocks, same rule as full episode)
  thumbnail.md
  youtube_title.md        (Shorts-style: shorter, punchier)
  hashtags.md
  qa_checklist.md
```

## Rules
- Never reuse the exact same `hook_id` from `curiosity_hooks.json` in a
  Short that a recent full Episode already used — check
  `world_state.json` chronology the same way full episodes do.
- A Short is not a trailer for the full episode — it must be a complete,
  satisfying moment on its own, even if it also links to a fuller episode.
- All character/Islamic-reference consistency rules from the full Episode
  profile still apply in full — Short format doesn't relax accuracy or
  visual-lock requirements, only length.

## Related Files
`phase1/docs/story/STORY.md`, `phase3/knowledge/story/curiosity_hooks.json`,
`phase3/knowledge/story/conflict_library.json`,
`phase3/knowledge/story/emotion_database.json`,
`phase1/docs/seo/COMPETITOR_STRATEGY.md`
