---
id: GOVERNANCE_VERIFICATION_PIPELINE
version: 1.0
status: production
depends_on: [phase1/docs/governance/review_workflow.md, phase2/data/database/review_queue.json]
last_updated: 2026-08-03
---

# verification_pipeline.md — Evidence & Verification, Not Human Judgment of Islamic Accuracy

Supersedes the former v2.9 human-review-pipeline document (v2.9), which incorrectly framed
episode approval as something the creator personally judges for Islamic
accuracy. **The creator is not Muslim and has no Islamic domain
knowledge — the pipeline must not assume otherwise.** This version
splits the gate into two genuinely different checks, done by two
genuinely different people.

## Two separate checks — never conflate them

### 1. Evidence completeness check (the creator can do this)
This does not require Islamic knowledge. It's a citation-completeness
audit: does every claim in the episode trace to a named source in
`phase2/data/islamic/*.json`, or is something stated without one? Fully
mechanical, produced automatically as `verification_report.md` (see
below) and readable by anyone.

### 2. Scholarly accuracy check (requires an external qualified reviewer)
Whether the cited sources are authentic, correctly translated, correctly
applied to the topic, and not misrepresenting a disputed area — this
genuinely requires Islamic scholarship. This is not a task for the
creator to attempt, and the pipeline must never imply it is. This is
what `scholarly_reviewed: true` on an individual entry in
`phase2/data/islamic/*.json` actually certifies, and it can only be set
by an actual qualified person, external to this pipeline.

## Pipeline flow
```
Repository (phase2/data/islamic/*.json, phase3/knowledge/concepts/)
        ↓
AI Retrieval (retrieval_ranking.md — ranks and selects sources)
        ↓
Story Generation (MASTER_PROMPT.md)
        ↓
Automatic Validation (rubric.md scoring + validate_repo.py)
        ↓
verification_report.md generated automatically (see schema below)
        ↓
Output Package delivered to creator
        ↓
Creator checks: are all claims cited? any warnings? (no Islamic
knowledge required — this is a completeness check, not a correctness one)
        ↓
If warnings exist or the creator wants confidence before publishing:
route to an external qualified Islamic reviewer
        ↓
External reviewer sets scholarly_reviewed: true on the specific entries
they've checked
        ↓
Publish
```

## Controlled Status Vocabulary — no false certainty (added v2.15)
Never output blanket statements like "All references accurate" or
"Zero fabricated content confirmed" unless every layer below actually
justifies it. Use these statuses explicitly, per layer, in every
`verification_report.md`:

```
Repository identity: PASS | FAIL
Source resolution: PASS | FAIL
Structural source consistency: PASS | SOURCE_MISMATCH
Semantic claim support: DIRECT_SUPPORT | INDIRECT_SUPPORT | INTERPRETIVE | UNSUPPORTED
Scholarly review: NOT COMPLETED | COMPLETE
Overall Islamic verification: VERIFIED | SUPPORTED | PARTIALLY_SUPPORTED | REVIEW_REQUIRED | UNSUPPORTED | SOURCE_MISMATCH | REPOSITORY_CONTEXT_UNAVAILABLE | UNKNOWN
```
**Fail-closed rule:** if any layer cannot be determined, the status is
`UNKNOWN` or `REVIEW_REQUIRED` — never silently promoted to `PASS` or
`VERIFIED` to let generation finish cleanly. An incomplete check is not
evidence of correctness.

## Semantic Claim Support — citation existence is not enough (added v2.15)
A cited source existing and being correctly formatted (`citation_verified`,
`source_verified` both true) does not by itself mean the source
actually supports the specific claim the script makes. Classify every
claim:
- **DIRECT_SUPPORT** — the source states the claim plainly (a dua's
  own translation used as the dua's own meaning).
- **INDIRECT_SUPPORT** — the source supports a broader or adjacent
  point that the claim narrows from (a general justice verse used to
  support "everyone gets a turn" — related, not identical).
- **INTERPRETIVE** — the claim requires real interpretive work to
  connect to the source (applying a decision-then-trust verse to a
  child finding a wallet — see the honesty-wallet episode's Claim 3 for
  a real worked example). Set `review_required: true`.
- **UNSUPPORTED** — no real connection; the claim must not ship as
  verified Islamic teaching regardless of how source-adjacent it sounds.
This is exactly the check that would have caught the `concept_honesty`
↔ `hd_002` stretch (a speech hadith used to imply a property-honesty
teaching) flagged during the wallet-episode's Smart Fallback — that was
caught by manual read at the time; this makes it a named, repeatable
category instead of something only caught by chance.

## Paraphrase ≠ Canonical Text — keep these four fields separate (added v2.15)
Never present a paraphrase as if it were Quran/hadith wording, and
never let quotation marks around a generated sentence imply Allah or
the Prophet ﷺ said those exact generated words. Four distinct things,
never interchangeable:
- **canonical_text** — the exact source-language text (Arabic), never
  regenerated or reconstructed from model memory during generation —
  retrieved verbatim from `arabic_text` in the repository record.
- **translation** — the repository's own stored/approved translation
  (`translation_simplified` field) — not re-translated on the fly.
- **child_paraphrase** — a simplified explanation for the target age,
  clearly distinct from the translation, never quoted as if it were the
  translation itself.
- **educational_interpretation** — the lesson the episode draws from
  the evidence — the furthest step from the source text, and the one
  most likely to need `review_required: true` per the Semantic Claim
  Support levels above.
Current schema note: `phase2/data/islamic/*.json` entries store
`arabic_text` and `translation_simplified` universally. Two entries
(`dua_005`, `qv_004` — the ones with genuinely distinct child-facing
wording already written for real episodes) now also carry
`child_paraphrase`/`educational_interpretation` as of v2.16. The
remaining 35 entries do not yet have these fields — they are not
fabricated to fill the schema; they're added only when a real,
distinct paraphrase already exists from actual use, per the no-mass-
data-generation rule. Tracked in `roadmap/planned_features.md` for
gradual, real population alongside future episodes.

## Readiness Dimensions (added v2.30) — five separate questions, never conflated
A package passing every automated check answers only the first of these:
- **technical_ready** — all required files present, validator PASS, character
  locks intact, no fabricated/mismatched claims. What `episode_consistency_check.py`
  actually proves.
- **religious_source_verified** — every religious claim's evidence has
  `citation_verified: true` and `source_verified: true`. Mechanical, not scholarly.
- **scholarly_review_required** — always `true` until a real qualified
  reviewer sets `scholarly_reviewed: true` on the specific entries used.
  Never set by this system, never by the creator.
- **character_assets_ready** — real approved visual/voice assets exist
  (per the character schema's `optional_asset_fields`) — currently
  `false` for everything, pending the Character Master Library.
- **publication_ready** — the actual gate for uploading anything. `true`
  only when ALL four above are satisfied. A `technical_ready: true`
  package is not publication_ready by itself — this distinction exists
  specifically so "the validator passed" is never mistaken for "safe to
  publish."

## Three independent fields replace the single `human_reviewed` flag (added v2.11)
Every entry in `phase2/data/islamic/*.json`, `islamic_vocabulary.json`,
and `phase3/knowledge/concepts/*.json` now carries three separate
booleans instead of one, because they answer three different questions:

- **`citation_verified`** — does this entry name a specific, real source
  (a book + page, a hadith collection + number, a verse reference)?
  `false` for entries that only say "Unknown source reference" or
  "General Islamic vocabulary, standard usage."
- **`source_verified`** — has that named source actually been checked
  against the entry's content (e.g. the OCR'd page genuinely says what
  the entry claims)? For this repository's extracted entries (dua_005,
  dua_006, qv_004, qv_005, prophet_yunus, and the vocabulary/concept
  entries derived from them), this was done during extraction — see
  `knowledge_builder_pipeline.md`. `false` wherever `citation_verified`
  is `false` (can't verify a source that isn't named).
- **`scholarly_reviewed`** — has an actual qualified Islamic scholar
  checked this entry for authenticity and correct application? This is
  the only one of the three that requires Islamic domain knowledge, and
  it is currently `false` on every entry in the repository — nothing
  has been scholar-reviewed yet.

A creator without Islamic knowledge can fully evaluate the first two
fields. Only the third requires the external reviewer step.

## `verification_report.md` — required per-episode output, full Evidence
& Risk schema (added v2.10, expanded to per-claim detail in v2.11)
Every episode's `output_package/<slug>/` must include this alongside
`validation_report.md` (which is the rubric quality score — a different,
already-existing file). One block per Islamic claim made in the episode:

```
# Verification Report — <episode title>

## Claim 1
Claim: "Allah is enough for us, and He is the best One to take care of things."
Evidence: dua_005 — Hisn al-Muslim, item 84, p.60
Source Type: Dua (Hadith-sourced supplication)
Authenticity: Named source, page-specific
citation_verified: true
source_verified: true
scholarly_reviewed: false
Interpretation Needed?: No — direct quote, not paraphrased meaning
Review Recommended?: Yes — scholarly_reviewed is still false

## Claim 2
[repeat per claim — including a claim with no real source, if one
somehow occurs despite retrieval_ranking.md's rules]
Claim: "Children should always do X because Islam requires it."
Evidence: No direct source found.
Source Type: AI inference
Authenticity: Unverified
citation_verified: false
source_verified: false
scholarly_reviewed: false
Interpretation Needed?: Yes
Review Recommended?: YES
Reason: Derived statement without an explicit primary source — do not
publish this claim as-is; either find a real citation or remove/reword
it as opinion rather than an Islamic ruling.

## Claims without a direct citation
[Restate here any claim from above with citation_verified: false, or
state "None found" explicitly — never silently omit this section.]

## Warnings
[Anything the automatic check couldn't resolve — e.g. two sources
disagree, a candidate had low retrieval-ranking confidence, a claim is
paraphrased further from the source than usual.]

## Evidence Summary
Total Claims: <n>
Direct Quran: <n>
Direct Hadith: <n>
Direct Dua: <n>
Repository Facts (vocabulary/concept, non-Quran/Hadith/Dua): <n>
AI Inference (no source — should be 0): <n>
Unverified Claims (citation_verified: false): <n>
Review Recommended: Yes/No

## What this report does NOT certify
This report confirms citation completeness (citation_verified,
source_verified) — every claim traces to a named, real source that's
been checked against its content. It does NOT certify
scholarly_reviewed — that requires the external qualified-reviewer step
above, and is currently false on every entry in this repository.
```

Reading the Evidence Summary alone answers "is this episode safe to
route forward" without opening the full per-claim table: if
`Unverified Claims` and `AI Inference` are both 0, citation-completeness
is solid; `Review Recommended` will still read `Yes` until
`scholarly_reviewed` is true somewhere, which is expected and not an
error state.

## What the creator's job actually is
1. Open `verification_report.md`. Read the **Evidence Summary** block
   first — if `Unverified Claims` and `AI Inference` are both 0, jump to
   step 2; if not, find those specific claims in the per-claim section
   above it.
2. Read the "Claims without a direct citation" section — if non-empty,
   that's a real gap; route back to generation or flag for review rather
   than publishing around it.
3. Read "Warnings" — same treatment.
4. Decide, per episode, whether the stakes justify getting an external
   qualified reviewer's sign-off before publishing (recommended for
   every episode at this channel's scale, cheap given the small dataset
   — see `review_workflow.md`'s practical note on batching this
   efficiently rather than per-episode).

## `review_queue.json` status update (v2.10)
Statuses remain Generated → Reviewed → Approved → Production, but
"Reviewed" now explicitly means "creator confirmed the verification
report has no missing citations or unresolved warnings" — not "creator
judged Islamic accuracy." "Approved" still requires
`scholarly_reviewed: true` on every cited Islamic entry, set only by an
external qualified reviewer, exactly as before — this part didn't change,
only who is expected to do the creator-facing check changed.

## Related Files
`phase1/docs/governance/review_workflow.md`,
`phase2/data/database/review_queue.json`,
`phase5/orchestration/planning/retrieval_ranking.md`,
`tools/package_episode.py`
