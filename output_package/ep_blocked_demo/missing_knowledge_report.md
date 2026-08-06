# Missing Knowledge Report — ep_blocked_demo

execution_mode: blocked
production_ready: false
version: v2.14

## Requested episode
Topic: "The Correct Ruling on [a specific, narrow, disputed fiqh
question with no repository presence at all]"
(This is a deliberately constructed demonstration case for
execution_modes.md's BLOCKED path — not a real production request.)

## Why this is BLOCKED, not ASSISTED
Smart Fallback (execution_modes.md) was run: searched
`phase3/knowledge/concepts/*.json` for the closest matching concept —
none of the 20 existing concepts (tawakkul, gratitude, honesty,
patience, kindness, forgiveness, generosity, humility, prayer,
respect_for_parents, cleanliness, courage, community, mercy, justice,
self_control, trustworthiness, perseverance, compassion_for_animals,
charity) relate to this specific disputed ruling closely enough to
support a genuine, real-evidence-backed adjacent story. Unlike the
`ep_honesty_wallet_assisted` case (where `concept_honesty` provided a
real fallback), there is no adjacent concept here with any real
evidence to fall back to.

| Missing Item | Reason | Repository Location | Files to Update | Estimated Fix Effort | Priority |
|---|---|---|---|---|---|
| Any Islamic reference on this specific topic | 0 matches repo-wide, and no adjacent concept provides a real fallback | phase2/data/islamic/*.json, phase3/knowledge/concepts/ | Would require a new source extraction AND a new concept package before any story is tellable | Not estimable without first identifying and sourcing real material | Critical |
| A disputed-ruling handling procedure | Even with a source, DESIGN_PRINCIPLES.md non-negotiable #3 requires disputed opinions never be presented as settled fact — this needs explicit multi-view framing, not just a citation | dispute_response.md, review_workflow.md | N/A — process guidance, not a data gap | N/A | High |

## No episode files were generated
Per execution_modes.md's BLOCKED MODE: this report is the only output.
Nothing was fabricated to fill the gap.
