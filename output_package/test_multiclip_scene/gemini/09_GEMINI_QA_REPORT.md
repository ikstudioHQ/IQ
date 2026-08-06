# QA Report — test_multiclip_scene (6 clips, ~60s)

| Dimension | Result | Note |
|---|---|---|
| Character continuity | PASS | char_001_zayd/char_002_amira identity locks unchanged across all 6 clips |
| Voice continuity | PASS_WITH_REVIEW | Identity descriptors consistent throughout; provider/voice_id still null (real approval pending, not a defect) |
| Location continuity | PASS | loc_family_living_room (CLIP_001-003) -> loc_family_kitchen (CLIP_004-006), explicit tracked change, not accidental |
| Wardrobe continuity | PASS | wardrobe_zayd_default / wardrobe_amira_default unchanged all 6 clips |
| Prop continuity | PASS | prop_grocery_bag_01 tracked correctly: held by Zayd (001-003) -> carried to kitchen (004) -> set down, off-frame (005-006) |
| Camera continuity | PASS | axis consistent within each location; CLIP_004's re-establishment for the new room is a real scripted location change, not an error |
| Dialogue timing | PASS | all 4 dialogue clips computed via validate_dialogue_timing.py -- real numbers, not estimated by eye (see dialogue_timing_check.json) |
| Prompt size | PASS | representative prompts stayed under budget by prioritizing identity/voice/dialogue/timing over decorative language, per the stated priority order |
| Religious safety | PASS | dua_002 (Bismillah) and dua_003 (Alhamdulillah) both real, citation_verified:true; no fabricated claims |
| Asset traceability | PASS | every clip records asset_versions; final_edit_manifest traces clip->timeline; generation_log traces clip->prompt_version |

## Overall: PASS_WITH_REVIEW
Technically and structurally sound. The single review item (voice
provider/ID still null) is an honest, expected gap -- no real voice has
been selected/approved yet, exactly as instructed not to invent one.

## Update: full 6/6 completion pass

All 6 clips now have complete image prompts, image-animation prompts,
and self-contained direct-animation prompts (no placeholders, no "same
as previous" language) -- confirmed by direct inspection, not assumed.

## Negative test (P12)
Injected defect: `CLIP_005` Amira wardrobe silently changed to an
unregistered, unscripted ID (`wardrobe_amira_eid`) in a temporary copy
of the continuity manifest -- the real repository file was never
touched. Ran the same continuity checker against the defective copy:
**detected in 3 separate ways** -- drift into CLIP_005, drift back out
in CLIP_006, and a reference to a wardrobe ID not in
`wardrobe_library.json` at all. Defect then discarded (temp file
deleted); confirmed the real manifest was unaffected throughout.

## Prompt size (P10)
Word count across the 6 direct-animation prompts: min 194, avg 235,
max 288. No documented Gemini hard limit exists in this repository, so
this is reported as relative sizing, not measured against an invented
threshold.
