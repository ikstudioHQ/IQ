---
id: PLANNING_EXECUTION_MODES
version: 1.0
status: production
depends_on: [phase5/orchestration/planning/retrieval_ranking.md, phase1/docs/governance/verification_pipeline.md, phase4/engine/quality/rubric.md]
last_updated: 2026-08-04
---

# execution_modes.md — Production / Assisted / Blocked

Replaces the binary PASS/STOP behavior at `MASTER_PROMPT.md` Step 14
with three outcomes. This does not add a new evidence system — it reuses
`retrieval_ranking.md` (for finding candidates), `verification_pipeline.md`
(for citation status), and `rubric.md` (for the quality gate) exactly as
they already exist. It only changes what happens with their results at
decision time.

## Repository Presence Guard — runs BEFORE everything else (added v2.15)
Before Step 2 (Load Configuration) — before retrieval, Smart Fallback,
Assisted Mode, curriculum resolution, character resolution, Islamic
evidence retrieval, story generation, image generation, or SEO
generation — run `tools/preflight_check.py`. It returns one of:

- **REPOSITORY_VERIFIED** — proceed normally.
- **REPOSITORY_INCOMPLETE** — required anchor files/directories missing.
- **REPOSITORY_VERSION_MISMATCH** — `VERSION_COMPATIBILITY.md`,
  `repository_manifest.json`, and `knowledge_index.json` disagree, or
  the prompt's expected version doesn't match the repo's declared one.
- **REPOSITORY_IDENTITY_UNVERIFIED** — version file unparseable.
- **REPOSITORY_CONTEXT_UNAVAILABLE** — no repository anchors found at all.

**Any status other than REPOSITORY_VERIFIED is an immediate BLOCKED
MODE outcome, full stop — before any content generation begins.**
This is not the same BLOCKED path as "Smart Fallback found nothing" —
it's a harder, earlier gate. Total or partial repository unavailability
must never be treated as an evidence gap and routed into Assisted Mode.
An agent with only `MASTER_PROMPT.md`'s text and no actual repository
files present does not have "partial evidence" — it has no repository,
and must stop, not improvise one. (This is the exact failure this rule
was written in response to — see `CHANGELOG.md` v2.15.)

## No Self-Seeding During Generation (added v2.15)
Generation must never repair its own missing evidence by creating
source-of-truth data mid-run. Prohibited during episode generation:
creating or modifying canonical Quran/Hadith/dua data, Islamic
concepts, curriculum topics, canonical character files, locked
character descriptions, or canonical vocabulary — even in-memory
placeholders that get treated as evidence for the rest of the run.
Missing information is recorded in `missing_knowledge_report.md` and/or
`repository_improvement_suggestions.md` as a proposal for later, human-
reviewed ingestion (`knowledge_builder_pipeline.md`). It never becomes
trusted evidence within the same generation run that discovered the gap.

## Read-Only Canonical Knowledge During Generation (added v2.15)
Canonical directories (`phase2/data/islamic/`, `sources/characters/characters/`,
`phase3/knowledge/concepts/`, `phase3/knowledge/curriculum/`) are
read-only during a generation run. Allowed to change:
`output_package/`, `generation_log.json`, `current_state.json`,
`world_state.json`, `last_episode.json`, `review_queue.json`. Verify
with `tools/episode_consistency_check.py snapshot` before generation
and `verify` after — any diff in a protected path is an automatic
`validation: FAIL, production_ready: false`, reported with the exact
file(s) that changed.

## Canonical Character Resolution — Never Reconstruct From Memory (added v2.15)
For each character the episode needs: `character_id` → the real file in
`sources/characters/characters/` → its locked description block →
inlined into prompts. If a named character (Zayd, Amira, Ummi Layla,
Nuri, or any future canonical character) cannot be resolved to a real
file, that is a BLOCK for that character (or the whole episode, if the
character is load-bearing) — never a silent decision to invent a
replacement design. Verify with
`tools/episode_consistency_check.py check-episode` after generation:
it byte-compares (whitespace-normalized) every locked block actually
used in `image_prompts.md`/`thumbnail.md` against the canonical file.

## Islamic Evidence Source Guard (added v2.15)
A Quran verse or hadith correctly recalled by the model is still not
repository evidence. For every claim used as verified production
evidence: `generated claim` → `source_id` → the real record in
`phase2/data/islamic/*.json` must resolve. If it doesn't resolve, it is
reported as a knowledge gap (`missing_knowledge_report.md`) — never
silently added to the repository or self-certified as verified within
the same run. Quran/hadith canonical text is retrieved verbatim from
the repository and copied exactly — never rewritten, regenerated, or
merged from fragments of different verses during generation (this is
literally what caused the 5:42 mismatch that prompted this section —
see `CHANGELOG.md` v2.15 for the full incident).

## The three modes

### 🟢 PRODUCTION MODE
Every Islamic claim the episode needs has a candidate with
`citation_verified: true` and `source_verified: true` (per
`verification_pipeline.md`). The curriculum topic node exists in
`available_topics.json`/`topic_graph.json`. Requested duration is within
`DESIGN_PRINCIPLES.md`'s 3–7 minute range. Generate the complete
28-file package normally. `scholarly_reviewed` may still be `false` —
that's a separate, later gate (`review_queue.json`'s `approved` status),
not a blocker on generation itself. Set `execution_mode: production` in
`validation_report.md`.

### 🟡 ASSISTED MODE
Some requested claims have no supporting evidence, but enough real,
verified evidence exists to tell a genuine, undiluted story about a
**supported adjacent claim** (see Smart Fallback below).

**What Assisted Mode is NOT (clarified v2.15):** repository
unavailable, repository inaccessible, repository incomplete at the
architectural level, the agent only has `MASTER_PROMPT.md`'s text with
no data files behind it, or the agent is relying on "likely" data it
remembers from a previous context rather than reading real files right
now. Any of those is the Repository Presence Guard's job (above) — it
resolves to BLOCKED before Assisted Mode logic is ever reached. Smart
Fallback only operates *inside* a verified repository, searching real
files that are actually present.

Generate the package using only claims that trace to real, cited sources — silently
dropping or rewording anything that would require inventing a ruling,
hadith, or verse. Produce all three of:
- `verification_report.md` (existing schema, per `verification_pipeline.md`)
- `missing_knowledge_report.md` (extended schema — see below)
- `validation_report.md`, with `status: assisted` and
  `production_ready: false`

Never silently ship an assisted episode as if it were fully requested —
the title, description, and `episode_summary.md` must reflect what was
actually generated, not the original request (e.g. "...Chose to Be
Honest," not "...Found a Lost Wallet," if the wallet/lost-property claim
itself has no evidence — see the worked example in
`examples/ep_honesty_wallet_assisted/`).

### 🔴 BLOCKED MODE
Only when **no safe adjacent claim exists** — Smart Fallback (below)
finds no concept with enough real evidence to tell any genuine story
related to the request. Produce `missing_knowledge_report.md` only. No
episode files are written. This is now the rare case, not the default —
under v2.13's behavior, everything that could reach Assisted was
stopping at Blocked instead.

## Decision procedure (runs at Step 14, replacing the old hard-stop)

```
1. Run Step 14 exactly as before: check every claim the requested
   topic needs against real, cited evidence.
2. If ALL pass with citation_verified + source_verified true, AND
   the topic node exists, AND duration is in range
   → PRODUCTION MODE. Continue Step 15 onward normally.
3. If some claims fail →  run Smart Fallback (below) before giving up.
4. If Smart Fallback finds a genuine, real-evidence-backed adjacent
   story → ASSISTED MODE. Generate using only what Smart Fallback
   surfaced. Write missing_knowledge_report.md documenting what was
   dropped and why.
5. If Smart Fallback finds NOTHING usable → BLOCKED MODE. Write
   missing_knowledge_report.md only.
```

## Smart Fallback (used by step 3-4 above)

1. **Search for the closest supported concept.** Use
   `phase3/knowledge/concepts/*.json` — match the requested topic's
   theme against existing `concept_id`s (e.g. "lost wallet honesty" →
   `concept_honesty`, already exists, already has a `recommended_default`).
2. **Search that concept's real related evidence** —
   `related_quran`/`related_hadith`/`related_duas`/`related_prophets`/
   `related_vocabulary`/`related_manners` fields, plus run
   `retrieval_ranking.md` normally over whatever's real and available.
3. **If the resulting evidence set is non-empty and can support a
   genuine story** (not just one isolated vocabulary word — needs at
   least a concept definition plus one Quran/hadith/dua/prophet
   reference with `citation_verified: true`), generate Assisted Mode
   using exactly that evidence, nothing more.
4. **Never fabricate to fill a gap Smart Fallback didn't close** — if
   the closest concept still doesn't have enough real evidence, that's
   Blocked Mode, not a license to invent.

This is the mechanism behind the worked example: the wallet episode's
specific "return lost property" and "Allah rewards honesty" claims had
zero evidence (confirmed — see `missing_knowledge_report.md`'s original
report), but `concept_honesty` itself has real evidence (`vocab_005`,
`vocab_006`, `qv_004`, `dua_005` all `citation_verified: true`) — enough
for a genuine, differently-scoped honesty story, which is what Assisted
Mode produces.

## Auto Duration Correction (Step 1, extended)

Requested duration outside `DESIGN_PRINCIPLES.md`'s 3–7 minute range no
longer fails Step 1. Instead:
```
requested_duration_sec: 600
repository_max_sec: 300
duration_adjusted: true
generated_duration_sec: 300
```
Log this in `generation_log.json` and in the episode's
`episode_summary.md`. Continue generation at the corrected duration.
This does not apply to violations that aren't simple range-clamping
(e.g. a request for an age-inappropriate duration structure) — those
still route through normal Step 1 validation.

## Draft Curriculum Mode (Step 13, extended)

If a concept package exists (a concept file (e.g. concept_honesty.json))
but no matching topic node exists in `available_topics.json`/
`topic_graph.json`, don't block on that alone:
```
status: draft_topic
repository_modified: false
```
Construct an in-memory draft topic object (concept's own
`recommended_age_range`, inferred prerequisites from
`ADR_003_curriculum_order.md`'s ordering logic) for use in **this
generation only**. Never write it into `available_topics.json` or
`topic_graph.json` automatically — that's a deliberate repository change
requiring the same process as any other topic addition (see
`knowledge_builder_pipeline.md`'s pattern). Log the missing node in
`missing_knowledge_report.md` under Priority: Medium (it doesn't block
generation, but it should still get a real topic node eventually so
future requests don't repeat this gap).

## Extended `missing_knowledge_report.md` schema

Replaces the plain-list format with a per-item table:

```
| Missing Item | Reason | Repository Location | Files to Update | Estimated Fix Effort | Priority |
|---|---|---|---|---|---|
| Hadith/ruling on returning lost property (luqatah) | 0 matches repo-wide | phase2/data/islamic/hadith.json | hadith.json (+ knowledge_index.json if new category) | ~30 min (extract from 40 Hadith an-Nawawi, per CATALOG.md) | Critical |
| Curriculum topic node for honesty | concept exists, topic node doesn't | phase2/data/database/available_topics.json, topic_graph.json | both files | ~10 min | Medium |
```
Priority levels: **Critical** (blocks the specific requested claim
entirely, no fallback), **High** (blocks Production Mode but Assisted
Mode covers it), **Medium** (doesn't block generation, e.g. Draft
Curriculum Mode gaps), **Low** (nice-to-have, e.g. a second supporting
source for something already covered once).

## `repository_improvement_suggestions.md` (new, generated at end of any Assisted/Blocked run)

Ranked, actionable only — no generic advice:
```
# Repository Improvement Suggestions — generated <date>, from run <episode_id>

## Critical
- Extract luqatah (lost property) hadith from
  en-p-al-arba3un-alnawawiia-abo-zakaria-annawawy-ppp.pdf (already
  catalogued, unextracted) into hadith.json. Unblocks: any future
  honesty-and-property topic. Effort: ~30 min per
  knowledge_builder_pipeline.md.

## Medium
- Add t_honesty to available_topics.json/topic_graph.json (concept
  already exists — see Draft Curriculum Mode note above). Effort: ~10 min.
```
Ranking mirrors the Missing Knowledge Report's Priority column but is
phrased as an action, not a gap — this file is what a creator reads to
decide what to fix next, distinct from the report's role of explaining
why a specific run was limited.

## Reused, not duplicated
This file adds decision logic on top of existing systems only:
`retrieval_ranking.md` (finding/ranking candidates),
`verification_pipeline.md` (citation status fields and
`verification_report.md`'s schema), `rubric.md` (the quality gate,
unchanged — Assisted Mode episodes still get scored, and a low score
still blocks packaging per the existing auto-reject rule),
`world_state.json` (diversity/moral-progression checks, unchanged),
`camera_language.json` (unchanged). No new evidence-scoring system was
created.

## Related Files
`phase5/orchestration/planning/retrieval_ranking.md`,
`phase1/docs/governance/verification_pipeline.md`,
`phase4/engine/quality/rubric.md`,
`phase5/orchestration/planning/knowledge_builder_pipeline.md`,
`phase2/data/database/review_queue.json`
