---
id: FAILURE_CONFUSING_DIALOGUE
version: 1.0
status: production
last_updated: 2026-07-30
---

# Failure Pattern: Confusing or Age-Inappropriate Dialogue

## What it looks like
Dialogue that's grammatically fine but requires more working memory or
vocabulary than the target age band can hold — a 3-year-old's episode
using sentence structures or abstract words appropriate for a 7-year-old.

## Why it happens
`RULES.md` and `DESIGN_PRINCIPLES.md` state "write for ages 2-8" as a
single instruction, but 2-year-olds and 8-year-olds have very different
vocabulary and sentence-complexity needs — a single blanket rule doesn't
differentiate. This is the same root gap that motivated
`CHILD_DEVELOPMENT_MATRIX.md`.

## How to avoid it
- Always resolve the specific age target (not just "2-8") before writing
  dialogue, and check it against `CHILD_DEVELOPMENT_MATRIX.md`'s
  sentence-length and vocabulary guidance for that exact age band.
- Read dialogue aloud (per `script_prompt.md`'s existing validation
  question) specifically listening for sentence length and clause count,
  not just tone.
- Watch for a common sub-pattern: dialogue that's simple in vocabulary
  but conceptually dense (e.g. explaining causality — "because... which
  means... so that...") — that's an age-inappropriate complexity even if
  every individual word is a word a toddler knows.

## Related Files
`phase4/engine/writing/dialogue_rules.md`,
`phase1/docs/curriculum/CHILD_DEVELOPMENT_MATRIX.md`
