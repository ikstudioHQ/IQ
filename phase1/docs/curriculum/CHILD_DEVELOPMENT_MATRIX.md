---
id: CURRICULUM_CHILD_DEVELOPMENT_MATRIX
version: 1.0
status: production
depends_on: [CURRICULUM.md, DESIGN_PRINCIPLES.md]
used_by: [AI Pipeline, Content Generator]
last_updated: 2026-07-30
---

# CHILD_DEVELOPMENT_MATRIX.md — Age-Specific Generation Rules

`DESIGN_PRINCIPLES.md` and `RULES.md` say "write for ages 2-8." This file
breaks that single instruction into three concrete age bands so
generation actually adapts per age instead of writing one register for
the whole range. `MASTER_PROMPT.md` Step 16 (Plan Episode) and
`script_prompt.md`/`dialogue_prompt.md` should resolve the specific age
target against this table before writing any dialogue or narration.

## Age 2-3 (Toddler)
- **Vocabulary:** ~50-200 root words the child likely already knows
  (concrete nouns: family members, animals, food, body parts). Introduce
  at most one brand-new word per episode, repeated 2-3 times in context.
- **Sentence length:** 3-6 words per sentence. Simple subject-verb-object
  only. No subordinate clauses ("because," "which," "so that" — avoid).
- **Moral complexity:** One-step cause-effect only ("sharing makes Amira
  happy"). No competing values, no ambiguity, no delayed consequence.
- **Attention span guidance:** Sub-beat variation every 15-20 seconds
  within any beat longer than 30 seconds (see `pacing_problem.md`).
- **Conflict type:** Simple sharing, simple waiting, simple "I want it
  now" — resolved within seconds of onscreen time, not minutes.

## Age 4-5 (Preschool)
- **Vocabulary:** ~200-800 words, can handle simple abstract feeling
  words (proud, worried, grateful) if shown through action first and
  named second. Up to two new vocabulary words per episode.
- **Sentence length:** 6-10 words per sentence. One subordinate clause
  is acceptable ("Zayd felt sad because he forgot his dua").
- **Moral complexity:** Two-step cause-effect, mild internal conflict
  ("I want to play, but Amira needs help first").
- **Attention span guidance:** Sub-beat variation every 20-30 seconds.
- **Conflict type:** Small disappointment, minor social friction between
  the two lead characters, resolved with a visible decision the child
  makes on-screen.

## Age 6-8 (Early Elementary)
- **Vocabulary:** 800+ words, can introduce a genuinely new concept word
  per episode with a clear in-story definition (e.g. "sabr" / patience).
- **Sentence length:** 8-14 words per sentence, up to two clauses.
  Can handle simple "if/then" reasoning stated aloud.
- **Moral complexity:** Gentle moral dilemma with a real (if small) cost
  to the right choice — not just "be nice and everything works out
  instantly." The character can feel genuine reluctance before choosing
  well.
- **Attention span guidance:** Sub-beat variation every 30-45 seconds;
  can sustain a single visual composition slightly longer than younger
  bands if the dialogue is actively developing.
- **Conflict type:** Values in mild tension (fairness vs. loyalty,
  honesty vs. kindness), resolved through the character's own reasoning
  rather than an adult simply telling them the answer.

## How this interacts with `knowledge_curriculum.json`
`knowledge_curriculum.json` already tags topics with an `age_range` /
`estimated_age`. This matrix is the *execution* layer underneath that
tagging — once an age is selected for a topic, this table governs how the
script is actually written at the sentence level, not just which topic is
selected.

## Related Files
`phase1/docs/curriculum/CURRICULUM.md`,
`phase3/knowledge/curriculum/knowledge_curriculum.json`,
`phase3/knowledge/failures/confusing_dialogue.md`,
`phase4/engine/quality/rubric.md` (dimension 7: Language Simplicity)
