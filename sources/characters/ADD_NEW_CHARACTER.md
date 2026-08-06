# Adding a New Character — Procedure

The library is extensible. Adding character #85+ never requires editing
existing character records.

1. Choose the next unused `character_number` (check
   `character_master_library.json`'s max `character_number` + 1).
2. Create the record: `character_id` (`char_NNN_slug`), `canonical_name`,
   `role_relation`, `age`, `voice_profile_text`, `canonical_image_prompt`,
   `turnaround_prompt`, `expression_prompt`. Use `null` for anything not
   yet supplied — never invent.
3. Import reference assets into `sources/characters/reference_images/`.
4. If speaking: add a `voice_profile` block. Leave `provider`/`voice_id`
   null until a real voice is selected and approved.
5. Run the duplicate-name/ID check (see the script pattern used for the
   84-character import — same logic, just diffed against the new count).
6. Run the visual-similarity review (manual, human judgment — this
   system does not do pixel-level comparison).
7. Run the voice-collision audit (`voice_collision_audit.json`'s
   keyword-overlap method — flags for review, never auto-resolves).
8. Validate against restrictions (`content_restrictions.json`) — confirm
   the character isn't a sacred/revered figure requiring special handling.
9. Set `approval_status: APPROVED` only after real human review.
10. `PRODUCTION_LOCKED` once approved assets exist and are frozen.
11. Append to `character_master_library.json`'s `characters` array — the
    array is scanned in full by retrieval, so appending one record makes
    it immediately available. No other file needs editing.

Status values: `DRAFT` → `ASSET_PENDING` → `VOICE_PENDING` →
`REVIEW_REQUIRED` → `APPROVED` → `PRODUCTION_LOCKED` → (eventually) `RETIRED`.
Never reuse a retired character's ID for a different character.
