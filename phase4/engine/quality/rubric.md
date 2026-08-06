---
id: QUALITY_RUBRIC
version: 1.0
status: production
depends_on: [DESIGN_PRINCIPLES.md, VALIDATION_MATRIX.md]
used_by: [AI Pipeline, Human Reviewers]
last_updated: 2026-07-30
---

# rubric.md — Quality Rubric Engine

`VALIDATION_MATRIX.md` and `qa_checklist.md` answer PASS/FAIL — did this
episode meet the non-negotiable bar. This file answers a different
question: **how good is it**, on a 0-10 scale per dimension, so quality
can be tracked and compared across episodes rather than only gated at a
binary threshold.

## The 10 dimensions

| # | Dimension | 0-3 (weak) | 4-6 (acceptable) | 7-8 (strong) | 9-10 (exceptional) |
|---|---|---|---|---|---|
| 1 | **Islamic accuracy** | Uncited or fabricated reference | Cited but not scholar-reviewed | Cited, `scholarly_reviewed: true`, age-appropriate framing | Above + adds meaningful child-friendly context beyond the bare citation |
| 2 | **Educational value** | No clear takeaway | One takeaway, weakly connected to the story | One clear takeaway, earned through the plot | Takeaway reinforces a prior lesson naturally (visible curriculum progression) |
| 3 | **Emotional clarity** | Flat or confusing emotional beats | Emotions stated but not shown | Emotions shown through action/expression, not narrated | Emotional arc has a distinct shift a 3-year-old could point to |
| 4 | **Story structure** | Missing or malformed beats | All 5 `STORY.md` beats present but rushed/uneven | Beats present and well-paced | Beats present, paced, *and* varied in rhythm (not identical shape to the last 5 episodes) |
| 5 | **Character consistency** | Contradicts `knowledge_characters.json` personality or `locked_description_block` | Minor personality drift, visuals correct | Personality and visuals both fully consistent | Above + character shows a specific, recognizable quirk unique to them |
| 6 | **Visual consistency** | Locked description block paraphrased or altered | Block copied correctly, generic scene composition | Block copied correctly, scene composition follows `phase1/docs/animation/ANIMATION.md` | Above + composition follows `phase4/engine/cinematography/camera_language.json`'s structured scene_type rules |
| 7 | **Language simplicity** | Sentences too long/complex for target age band (see `CHILD_DEVELOPMENT_MATRIX.md`) | Mostly appropriate, a few adult-register words | Fully appropriate for target age | Appropriate *and* introduces exactly one new vocabulary word with a natural in-context definition |
| 8 | **Parent friendliness** | Nothing for an adult viewer to engage with | Inoffensive but forgettable for the accompanying parent | Contains a moment/line that lands for a parent too | Above + reinforces a value the parent would want repeated at home |
| 9 | **Child engagement** | No hook, no curiosity driver | Hook present but generic | Hook lands within the first 8 seconds (see `COMPETITOR_STRATEGY.md` Step 5) | Above + a mid-episode pattern-interrupt keeps the 2-minute conflict beat from feeling like one long block |
| 10 | **Production readiness** | Missing required output files | All 27 output files present, some thin | All present and complete | All present, complete, and `editing_notes.md` gives an unambiguous assembly order |

## Scoring
- Score each dimension 0-10. Sum and divide by 10 for an overall score
  out of 10.
- **Below 6.0 overall, or any single dimension at 0-3:** do not package
  as production-ready — matches and extends `MASTER_PROMPT.md`'s existing
  confidence-score gate (aggregated confidence ≥ 85/100 required).
- **6.0-7.9 overall:** ship-able, log in `generation_log.json` with the
  per-dimension breakdown so patterns of weakness are visible across
  episodes (e.g. "visual consistency keeps scoring low" is a signal to
  revisit `ADR_002_visual_style.md`'s implementation, not a one-off note).
- **8.0+ overall:** candidate for `examples/` as a reference episode.

## Content Quality Scorer — Automatic Reject Gate (added v2.7)
This makes the "Below 6.0 overall, or any single dimension at 0-3" rule
above an actual blocking check, not just guidance:
- Compute the overall score (sum ÷ 10) after all 10 dimensions are
  scored in `validation_report.md`.
- **Auto-reject conditions** (episode must not be packaged, full stop,
  no override): any single dimension scores 0-3, OR dimension 1
  (Islamic accuracy) scores below 7, OR the overall score is below 6.0.
- **Warn-but-proceed conditions**: overall 6.0-7.4 — package, but flag
  in `validation_report.md` for the creator to spot-check before upload.
- On auto-reject, `MASTER_PROMPT.md`'s Failure Handling applies: report
  which dimension(s) failed and why, do not silently retry with lowered
  standards, do not package a partial/degraded output_package.
- This is separate from, and stricter than, the general aggregated
  confidence-score floor of 85 already in `MASTER_PROMPT.md`'s
  "Confidence Scores" section — that floor covers pipeline-execution
  confidence (did the right files load); this gate covers output
  *quality* once generation completes.

## Relationship to other quality files
- `VALIDATION_MATRIX.md` / `qa_checklist.md` = binary gate (must pass to
  ship at all).
- `rubric.md` (this file) = graded score (how good, tracked over time).
- `phase3/knowledge/failures/*.md` = specific anti-patterns to actively
  avoid, informed by low rubric scores on past episodes.

## Related Files
`VALIDATION_MATRIX.md`, `phase4/engine/checklists/qa_checklist.md`,
`phase3/knowledge/failures/`, `phase1/docs/curriculum/CHILD_DEVELOPMENT_MATRIX.md`
