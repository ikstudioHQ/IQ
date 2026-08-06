---
id: FAILURE_WEAK_THUMBNAIL
version: 1.0
status: production
last_updated: 2026-07-30
---

# Failure Pattern: Weak / Low-CTR Thumbnail

## What it looks like
A technically correct thumbnail (right character, right colors) that
still underperforms on click-through because it doesn't read clearly at
small size or doesn't signal an emotional hook.

## Why it happens
`thumbnail_template.md`'s rules (large expressive eyes, warm pastel,
readable text 80-120px) are necessary but not sufficient — they describe
brand compliance, not attention-grabbing composition. A thumbnail can
follow every brand rule and still be visually flat if the character's
expression is neutral rather than reacting to something, or if the
composition is centered/static rather than showing a moment of tension
or joy.

## How to avoid it
- The thumbnail should capture the episode's emotional peak (the
  conflict moment or the joyful resolution), not a generic "character
  smiling at camera" pose — cross-reference `phase1/docs/seo/COMPETITOR_STRATEGY.md`
  Step 2's thumbnail-composition-matching guidance.
- Generate 2-3 thumbnail variants per episode (composition, not brand)
  and pick the one with the clearest single focal point — a full A/B
  variant requirement should be added to `thumbnail_prompt.md` once the
  channel has enough views to actually A/B test.
- Avoid identical thumbnail compositions across consecutive episodes —
  check `world_state.json` chronology the same way as the repeated-story
  pattern above.

## Related Files
`phase4/engine/thumbnails/thumbnail_template.md`,
`phase4/engine/prompts/thumbnail_prompt.md`,
`phase1/docs/seo/COMPETITOR_STRATEGY.md`
