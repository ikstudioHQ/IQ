# Voice Collision Method (v2.0, weighted)

## Why the v1 coarse method was replaced
The original 4-band method (age/gender/pitch/pace, each worth 1 point)
flagged 1233/3486 pairs — too noisy, because it weighted a generic
adjective match ("warm") the same as an identity-defining property
(pitch). Replaced.

## v2 weighted method
Score = weighted_sum / max_possible_score, where:
- `age_band` match: 3.0 (child/teen/adult/elder — identity-defining)
- `gender_voice_class` match: 3.0 (only counted when both specified)
- `pitch_center` match: 2.5 full, 1.25 for adjacent band (ordinal 1-5)
- `distinctive_descriptor_words` overlap ratio × 2.0 — **generic words
  excluded** (warm, gentle, kind, soft, clear, friendly, etc. — these
  appear across dozens of characters and carry no identity signal)
- `pace` match: 0.5 (low weight, most performances allow pace variation anyway)

Thresholds: ≥0.85 CRITICAL, ≥0.70 HIGH, ≥0.55 MODERATE, below not flagged.

## Real, honest result
Old method: 1233/3486 flagged. New method: 1141/3321 (82 real speaking
characters after fixing the Nuri/Boo-Boo non-speaking miscount).
**Only a modest improvement** — the underlying limitation is genuine:
the supplied `voice_profile_text` for most SUPPORTING/BACKGROUND
characters only really specifies age+gender+rough pitch, with no
further distinguishing detail. No text-analysis method can manufacture
distinctiveness that was never supplied. This is a real, honest
finding, not a method failure to fix with more cleverness — it's a
signal that **real audio auditioning is required** for anything beyond
CORE, which is exactly why this pass builds the review queue and
priority tiers rather than claiming the problem is solved.

## What IS solved
Zero CORE-vs-CORE CRITICAL collisions — the 5 characters actually
appearing constantly across built episodes (Zayd, Amira, Ummi Layla,
Baba Ahmad, Dada Yusuf) are genuinely voice-distinct from each other by
this method. That's the practically important result.
