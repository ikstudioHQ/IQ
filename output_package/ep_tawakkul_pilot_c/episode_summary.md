# Episode Summary — Tawakkul Pilot Test (Test C)

execution_mode: assisted
production_ready: false
status: TEST / NOT FINAL FOR PUBLICATION

**Age:** 5-7 | **Characters:** Zayd, Amira | **Environment:** env_home
**Core Concept:** Tawakkul — real evidence: qv_004, qv_005 (Quran), dua_005, dua_006 (Dua) — the richest-covered concept of the 3 tests, combined Quran+Dua as requested.

**Retrieval trace — diversity-aware, not the naive default:**
concept_tawakkul's recommended_default points to cf_001 ("lost toy") —
but `examples/ep_tawakkul_lost_toy/` already used cf_001 for this exact
concept. Per retrieval_ranking.md's diversity penalty on repeat use,
selected **cf_004** ("waiting impatiently for something") instead — a
real alternative from the same concept's related_conflicts, not
invented. This is what genuine diversity-aware retrieval should do;
naively reusing the recommended_default would have produced a
near-duplicate of the existing episode (see cross-episode comparison).

Zayd waits impatiently for Baba Ahmad to come home with a promised
surprise, and learns tawakkul — doing what he can, then trusting Allah
with the timing.
