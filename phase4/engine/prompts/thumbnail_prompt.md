# Thumbnail Prompt — Prompt Module

> Version: 1.1 | Owner: Islamic Kids Studio AI System | Last Updated: 2026-07-30

---

# THUMBNAIL PROMPT — Thumbnail Image Generation

## Purpose
Generates image prompts for episode thumbnails.

## Inputs
- Episode title
- Character IDs
- Scene setting (from `WORLD.md`)
- Brand colors (from `BRAND.md`)
- Age group

## Outputs
- Image prompt for thumbnail generation
- Style reference confirmation
- Composition description

## Rules
- Use brand colors: mint, peach, cream, lavender, soft blue.
- Show characters with big expressive eyes.
- Keep composition simple and clear.
- Use warm, inviting lighting.
- Include the episode number or main concept clearly.
- Make it merchandise-friendly.
- Ensure clear readability at small sizes.

## Template
"A warm, colorful thumbnail for [Title]. Main character [Name] in [Setting], with big expressive eyes, soft rounded shapes, warm pastel colors (mint, peach, cream), gentle lighting, simple composition, child-friendly, merchandise-ready. Style: cute, soft, warm, educational."

## Thumbnail Intelligence (added v2.7)
Beyond brand compliance (colors, shapes, lighting above), these decisions
actually drive click-through and must be made deliberately per episode,
not defaulted:
- **Emotion selected** — pick the single strongest emotion from the
  episode's peak moment (cross-reference `emotion_database.json`), not a
  generic smile. A thumbnail showing *worry-then-relief* implied through
  expression outperforms a flat happy face for curiosity-driven CTR.
- **Facial expression intensity** — exaggerate slightly beyond the
  in-episode expression (thumbnails are read at a glance, subtlety is
  lost at small size) while staying within `DESIGN_PRINCIPLES.md`'s
  gentle/non-alarming bounds.
- **Contrast** — the main character must be the highest-contrast element
  against the background; if the brand palette's pastels risk low
  contrast, darken or saturate the immediate background behind the
  character's face specifically, not the whole scene.
- **Composition** — character face/eyes in the upper two-thirds
  (standard thumbnail eye-line), enough negative space for title-safe
  text overlay if `SEO.md` calls for on-thumbnail text for this episode.
- **Curiosity gap** — the thumbnail should raise a question the title
  answers (or vice versa) — never show the full resolution in the
  thumbnail image itself.
- **Title alignment** — confirm the thumbnail's implied emotion matches
  `youtube_title.md`'s tone; a mismatch (calm thumbnail, urgent title, or
  the reverse) reads as clickbait and undermines trust for this audience
  specifically (see `MODERATION.md` / parent-trust considerations).
- Generate this as **2-3 composition variants** per episode (same
  character/scene, different expression or crop) rather than one — see
  `qa_checklist.md`'s A/B thumbnail item.

## Related Files
`BRAND.md`, `WORLD.md`, `CHARACTER.md`,
`phase3/knowledge/story/emotion_database.json`,
`phase1/docs/seo/COMPETITOR_STRATEGY.md`
