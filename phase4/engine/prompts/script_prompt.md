# Script Prompt — Prompt Module

> Version: 1.1 | Owner: Islamic Kids Studio AI System | Last Updated: 2026-07-30

---

# SCRIPT PROMPT — Dialogue & Script Generation

## Purpose
Generates dialogue, narration, and script content for Islamic Kids Studio episodes.

## Inputs
- Story prompt output
- Character profiles (`knowledge_characters.json`)
- Voice rules (`VOICE.md`)
- Language dictionary (`pronunciation_dictionary.json`)
- Age group

## Outputs
- Full script with narration and dialogue
- Scene directions (simple)
- Pronunciation markers for Islamic terms
- Emotion notes for voice actors

## Dialogue Rules
- Short spoken sentences.
- Conversational English.
- No robotic language.
- No repetitive dialogue.
- Every line contributes something new.
- Consistent character speaking styles.
- Emotional warmth in every line.

## Narration Rules
- Warm, friendly, never robotic.
- Short sentences.
- Show the action, don't over-explain it.
- Reference the visual without describing everything.
- Use emotional language naturally.

## Validation
- Read the script aloud. Does it sound natural?
- Are Islamic terms pronounced correctly?
- Do characters sound like themselves?
- Is there any filler, repetition, or robotic language?

## Related Files
`STORY.md`, `VOICE.md`, `LANGUAGE.md`, `CHARACTER.md`


## Schema Validation
Required Markdown: `DESIGN_PRINCIPLES.md` (Constitution), `phase1/docs/story/STORY.md`. Required JSON: `phase2/data/language/pronunciation_dictionary.json`. Optional: `phase2/data/language/tts_dictionary.json`.

## Fallback Behaviour
If required files are missing, load `MASTER.md` and confirm minimum viable inputs before stopping pipeline. Log error in `generation_log.json`. Do not generate with incomplete dependencies.
