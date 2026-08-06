---
id: CHARACTERS_GUEST_FRAMEWORK
version: 1.0
status: production
depends_on: [phase1/docs/decisions/adr/ADR_001_character_system.md, phase1/docs/decisions/adr/ADR_002_visual_style.md]
last_updated: 2026-08-01
---

# GUEST_CHARACTERS.md — Bringing In a Guest/Collab Character Safely

Cross-promotion with another Islamic creator is a real growth lever, but
the locked-cast system (`ADR_001_character_system.md`,
`ADR_002_visual_style.md`) has no defined way to introduce an outside
character without either (a) breaking the "only these six characters,
locked description blocks" rule, or (b) recreating the exact
two-character-system conflict `ADR_001` was written to prevent.

## The rule: guests are visitors, never additions to the locked cast
A guest character:
- **Never gets a `locked_description_block`** in `sources/characters/characters/`
  and never gets an entry in `knowledge_characters.json`,
  `active_characters.json`, or `character_versions.json` — those files
  stay reserved for the six permanent cast members.
- **Appears only in the specific collab episode(s)**, described fresh in
  that episode's `image_prompts.md`/`animation_directions.md` using
  whatever visual reference the collaborating creator provides (their
  own locked description, if they have one, used as-is for consistency
  with their own content — not restyled into this channel's Pixar/
  Illumination render language unless they agree to that).
- **Does not appear in `world_state.json`'s ongoing continuity** —
  no `character_lessons_learned` entry, no recurring friendship tracking.
  A guest is a one-time event, not a new permanent relationship in the
  Zayd/Amira world.
- **Gets a a guest-appearance log entry (conceptual filename; created only when the guest workflow is instantiated) log entry instead** (create this file
  the first time a guest episode happens — not needed until then): guest
  name, collaborating channel, episode ID, date. This is provenance
  tracking, not a character system.

## Episode-level rules
- A guest episode still follows the normal `MASTER_PROMPT.md` pipeline —
  same 5-beat structure, same Islamic-reference sourcing rules, same
  `human_reviewed` gate. Guest status affects only the character-data
  layer above, not content-quality or accuracy standards.
- Credit the collaborating creator clearly in `description.md` and
  `youtube_title.md` per normal collab-disclosure practice.
- Confirm the collaborating creator's own content is consistent with
  `DESIGN_PRINCIPLES.md`'s non-negotiables before agreeing to a collab —
  same trust-transfer risk as `SPONSORSHIP_POLICY.md` describes for
  brand sponsors, applied to content partners instead.

## Related Files
`phase1/docs/decisions/adr/ADR_001_character_system.md`,
`phase1/docs/decisions/adr/ADR_002_visual_style.md`,
`phase1/docs/community/SPONSORSHIP_POLICY.md`
