# Story Prompt — Prompt Module

> Version: 1.1 | Owner: Islamic Kids Studio AI System | Last Updated: 2026-07-30

---

# STORY PROMPT — Story Generation Module

## Purpose
Generates the narrative structure for Islamic Kids Studio episodes.

## Inputs
- Topic ID (from `available_topics.json`)
- Age group
- Series ID
- Character IDs (from `active_characters.json`)
- Curriculum requirements (from `CURRICULUM.md`)
- Islamic reference (from `ISLAMIC.md` or `quran_verses.json`)

## Outputs
- Episode title
- Story outline (5 sections)
- Moral statement
- Character actions
- Scene descriptions

## Rules
- Show, don't tell.
- Every sentence adds value.
- No filler.
- No robotic transitions.
- Write like a professional children's author.
- Write for ages 2-8 while engaging parents.
- Use emotional storytelling.
- Maintain consistent character personalities.

## Story Structure Template
1. Warm opening (15 sec): Character in a warm scene, gentle action.
2. Gentle conflict (2 min): A small problem appears. Character responds with feeling.
3. Character response (1 min): Character tries something kind, gentle, or brave.
4. Resolution with Islamic value (1 min): The value is shown through action, not explained.
5. Closing dua/song (30 sec): Gentle closing with a warm dua or short song.

## Validation
- Does the story teach one clear value?
- Is the conflict gentle and age-appropriate?
- Are character actions consistent?
- Does the Islamic value feel earned?
- Is the language conversational and natural?

## Related Files
`STORY.md`, `CHARACTER.md`, `WORLD.md`, `CURRICULUM.md`


## Schema Validation
Required JSON: `phase3/knowledge/characters/knowledge_characters.json`, `phase3/knowledge/world/knowledge_world.json`, `phase3/knowledge/curriculum/knowledge_curriculum.json`. Optional: `phase2/data/islamic/duas.json` (if story includes dua).

## Fallback Behaviour
If required files are missing, load `MASTER.md` and confirm minimum viable inputs before stopping pipeline. Log error in `generation_log.json`. Do not generate with incomplete dependencies.
