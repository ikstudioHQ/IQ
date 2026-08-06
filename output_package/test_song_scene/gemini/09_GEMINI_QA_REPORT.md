# QA Report — test_song_scene

| Dimension | Result | Note |
|---|---|---|
| Lyrics timing | PASS | each phrase fits its 10s clip at phrase boundaries, no mid-word cuts |
| Voice identity | PASS_WITH_REVIEW | consistent descriptors, provider/ID still null (expected) |
| Character consistency | PASS | same char_001_zayd/char_002_amira, same wardrobe locks as cartoon episodes -- no separate "song character" |
| Location continuity | PASS | loc_family_kitchen, single location, no drift |
| Movement | PASS | gentle swaying, natural, family-friendly |
| Camera | PASS | specified for both clips |
| Religious restrictions | PASS | lyrics paraphrase real gratitude concept (concept_gratitude, dua_002/003-adjacent), no fabricated quotation, no restricted content |
| Editing handles | PASS | clean cut CLIP_001->002, fade out at end |

## Overall: PASS_WITH_REVIEW (same honest voice-approval gap as the cartoon test)
