# ADR_004 — Prompt Strategy: Single Master Prompt + Retrieval Index, Not Many Independent Prompts

**Status:** accepted
**Date:** originating design predates this repository; formally recorded here

## Problem
An AI agent needs one clear entry point to generate a complete episode
package from a single topic input, without the user manually invoking 25
separate generation steps.

## Decision
`MASTER_PROMPT.md` is the single orchestration entry point. It does not
embed all content-generation logic itself — it directs the agent through
20 automatic steps that load specific files on demand via
`knowledge_index.json` (a concept→file-path retrieval index), delegating
actual generation work to 14 smaller, focused prompt modules in
`phase4/engine/prompts/` (`story_prompt.md`, `script_prompt.md`, etc.),
each with its own Purpose/Inputs/Outputs/Rules/Validation/Schema/Fallback
structure.

## Alternatives considered
1. **One giant prompt containing all generation instructions inline.**
   Rejected — harder to maintain (a change to dialogue rules would require
   editing a monolith), harder to reason about which rules apply to which
   output, and wastes context loading irrelevant instructions for every
   generation step (e.g. loading full SEO-writing instructions while
   generating character turnaround art prompts).
2. **Fully independent prompts with no shared orchestration**, requiring
   the user to manually run each of the 14 prompt modules in sequence.
   Rejected — directly contradicts the stated goal of "one topic in,
   complete project out" with zero manual steps.
3. **Load the entire repository into context on every run** rather than
   using a retrieval index. Rejected explicitly in `MASTER_PROMPT.md`
   Step 11 ("The system must NOT load the entire repository") — this
   controls token cost and reduces the chance of irrelevant/contradictory
   content influencing a given output.

## Consequences
- `knowledge_index.json` must be kept accurate — every new knowledge file
  needs an index entry, or the retrieval-only loading strategy silently
  misses it (this was the root cause of the broken `prophets` reference
  fixed in v2.3 — see `CHANGELOG.md`).
- The 14 sub-prompts must stay structurally consistent with each other
  (same section headings) so an agent generalizes across them correctly
  — enforced by `phase4/engine/checklists/qa_checklist.md` and spot-checked
  manually during review (`review_workflow.md`).
- This architecture has real per-run overhead (`MASTER_PROMPT.md` itself
  plus 4-5 cached core docs load before any content generation begins) —
  accepted as the cost of consistency and hallucination prevention,
  measured against the alternative of an under-specified, inconsistent
  pipeline.

## Source
`MASTER_PROMPT.md` "AUTOMATIC STEP 11", "KNOWLEDGE INDEX USAGE (MANDATORY)".
