# ADR_002 — Visual Style: Locked-Text-Block Pixar/Illumination-Style System

**Status:** accepted
**Date:** 2026-07-30 (originating design predates this repository's audit; formally recorded here)

## Problem
AI-generated visual content is prone to character drift — the same named
character looking meaningfully different from image to image or episode
to episode, because natural-language descriptions get paraphrased,
summarized, or reinterpreted by whatever model renders them.

## Decision
Every main character has an immutable **locked description block**
(`sources/characters/characters/*.md`) that must be copied
character-for-character, word-for-word, into every scene/image/animation
prompt that includes that character — never paraphrased, shortened, or
reworded. A shared **universal render suffix** (Pixar/Illumination-style
3D, specific render engine language, consistent lighting description) is
appended once per scene, not once per character, when multiple characters
appear together. Real turnaround reference images
(`assets/characters/*.jpeg`) back each locked block as ground truth.

## Alternatives considered
1. **Loose natural-language character descriptions, reworded per scene
   for variety.** Rejected — this is the standard failure mode for
   AI-generated series content; visual consistency was explicitly named
   as a core brand requirement (`DESIGN_PRINCIPLES.md`: "consistent
   character personalities," "clear silhouettes," merchandise-readiness).
2. **Reference-image-only (no text description), relying purely on
   image-to-image conditioning.** Rejected — not all downstream
   image/animation tools support image conditioning equally well, and a
   text block travels with the repository regardless of which generation
   tool is used that month.

## Consequences
- Any new character added in the future must follow the same pattern:
  generate a MASTER TURNAROUND PROMPT first, lock the resulting reference
  image and text block together, and never edit the locked block in
  place — a design change requires a new versioned file (e.g.
  a new versioned character file (e.g. an incremented filename)) per `deprecation_policy.md` and `character_version_lock.md`.
- Prompt length cost: every scene prompt involving a character carries
  ~150-200 words of locked description overhead. Accepted as necessary
  for consistency; not something future maintainers should "simplify."

## Source
`sources/characters/Islamic_Kids_Studio_Character_Prompts.txt`,
"CONSISTENCY RULES" section (original creator instructions).
