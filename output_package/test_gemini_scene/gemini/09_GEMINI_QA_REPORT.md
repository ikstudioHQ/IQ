# Gemini QA Report — test_gemini_scene

| Check | CLIP_001 | CLIP_002 |
|---|---|---|
| <=10 seconds | PASS (10.0s) | PASS (10.0s) |
| Dialogue timing valid (within 2-9s window) | PASS (2.5-5.8s) | PASS (2.0-5.2s) |
| Dialogue fits naturally, no speed-up needed | PASS | PASS |
| Character IDs valid | PASS (char_001_zayd, char_002_amira both in master library) | PASS |
| Character locks present | PASS | PASS |
| Voice locks present for speaking characters | PASS | PASS |
| No voice collision | PASS (Zayd/Amira not in voice_collision_audit.json's flagged pairs) | PASS |
| No identity drift | PASS (locks match master library verbatim) | PASS |
| No unexplained wardrobe drift | PASS (both "default", unchanged clip-to-clip) | PASS |
| Continuity valid | PASS (CLIP_002 correctly inherits CLIP_001's ending state) | — |
| Camera specified | PASS | PASS |
| Ending frame specified | PASS | PASS |
| Religious sources valid | PASS (dua_003, real citation_verified:true) | PASS (no religious claim, correctly empty) |
| Restrictions clean | PASS | PASS |
| Image prompt corresponds to animation prompt | PASS | PASS |
| Direct-animation prompt self-contained | PASS (full character/voice locks inline, no "same as before" language) | PASS |
| No unsupported asset path | **FLAG** — voice_id, provider, TTS fields all null (expected — not yet supplied, per instruction not invented) | same |
| No missing required field | PASS for all fields this test populates | PASS |

## Overall: PASS WITH EXPECTED GAPS
Technically sound and internally consistent. Not production-final because
voice_id/provider/TTS fields are honestly null (no real voice has been
selected/approved yet) and reference images are "supplied_unapproved_pending_review",
not yet confirmed by human review. Both gaps are expected at this stage,
not defects.

## Real gap found during this QA pass
`loc_zayd_home_living_room` was used as a location reference but has no
registered location record (per P32's location-master-lock system) —
this test used it informally. A real location library was not built
this pass; flagged for the next scoped addition, not fabricated here.
