---
id: FAILURE_REPEATED_STORY
version: 1.0
status: production
last_updated: 2026-07-30
---

# Failure Pattern: Repeated / Formulaic Story

## What it looks like
Two or more episodes share the same conflict shape, same character pairing,
and same resolution beat closely enough that a regular viewer (or parent)
notices the repetition within a few episodes of each other.

## Why it happens here specifically
Confirmed by direct audit of the seed data: `phase2/data/islamic/` holds
only 3-8 entries per category (duas, hadith, Quran verses, manners), and
`knowledge_world.json` only defines 5 environments. Every episode draws
from the same small pool. At current data volume, the pipeline runs out
of genuinely distinct source material within roughly the first 10-20
episodes, even though the 5-beat story structure itself
(`STORY.md`) is sound.

## How to avoid it
- Before generating a new episode, check `world_state.json`'s
  `episode_chronology` and `recurring_locations_used` — if the same
  Islamic reference or environment has been used in the last 3 episodes,
  actively pick a different one even if it's not the "obvious" choice
  for the topic.
- Treat the Knowledge Depth expansion (adding more duas/hadith/environments/
  props/story-conflict variations) as a prerequisite for scaling past
  ~15-20 episodes, not an optional nice-to-have.
- Vary *which* character initiates the conflict — don't let the same
  character always be the one who forgets/struggles and the other always
  be the one who reminds/helps.

## Related Files
`phase1/docs/story/STORY.md`, `phase2/data/database/world_state.json`,
`phase4/engine/quality/rubric.md` (dimension 4: Story Structure)
