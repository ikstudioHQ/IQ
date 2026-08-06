# Verification Report — Zayd's Lost Toy

This report requires no Islamic domain knowledge to read or act on. It
checks citation completeness and content-match (citation_verified,
source_verified). It does NOT certify scholarly_reviewed — that requires
an external qualified Islamic reviewer (see verification_pipeline.md).

## Claim 1
Claim: "Hasbunallahu wa ni'mal wakeel" / "Allah is enough for us, and He
is the best One to take care of things"
Evidence: dua_005 — Hisn al-Muslim (en_Hisn_El_Muslim.pdf), item 84,
p.60, footnote 52
Source Type: Dua (Hadith-sourced supplication)
Authenticity: Named source, page-specific, OCR-confirmed against
original text
citation_verified: true
source_verified: true
scholarly_reviewed: false
Interpretation Needed?: No — direct quote, not paraphrased meaning
Review Recommended?: Yes — scholarly_reviewed is still false

## Claim 2
Claim: "let's ask Allah to help us... after you do your best" (Ummi
Layla's framing of tawakkul in the script)
Evidence: qv_004 — Quran 3:159, cited via Hisn al-Muslim p.53, footnote 41
Source Type: Direct Quran Reference
Authenticity: Named source, specific verse and footnote
citation_verified: true
source_verified: true
scholarly_reviewed: false
Interpretation Needed?: Yes — the script paraphrases the verse's meaning
into a child-directed instruction rather than quoting it directly; the
underlying verse reference itself is exact
Review Recommended?: Yes — both for scholarly_reviewed status and to
confirm the paraphrase doesn't distort the verse's meaning

## Claims without a direct citation
None found. Every specific Islamic claim in the script traces to Claim 1
or Claim 2 above. General narrative color (Zayd playing at the park,
Amira remembering the bag) is not an Islamic claim and doesn't require one.

## Warnings
- Both cited sources have `scholarly_reviewed: false`. Expected at the
  current repository stage (see review_queue.json) — this is the reason
  the episode is not yet at `approved` status, not an unexpected problem
  with this specific episode.
- The Arabic subtitle translations of surrounding narrative dialogue
  (subtitles_ar.srt) beyond the dua itself are original translations
  produced for this episode, not sourced from a published translation —
  standard practice for original dialogue, noted here for transparency.

## Evidence Summary
Total Claims: 2
Direct Quran: 1
Direct Hadith: 0
Direct Dua: 1
Repository Facts (vocabulary/concept, non-Quran/Hadith/Dua): 0
AI Inference (no source — should be 0): 0
Unverified Claims (citation_verified: false): 0
Review Recommended: Yes (scholarly_reviewed is false on both claims — not
an "unverified" issue, a "not yet scholar-checked" one)

## What this report does NOT certify
Citation completeness only (citation_verified, source_verified — both
true on both claims). Scholarly accuracy of dua_005 and qv_004 —
correct transliteration, correct application to this context, no
scholarly dispute — requires the external qualified-reviewer step in
verification_pipeline.md before this episode can move to `approved`.
