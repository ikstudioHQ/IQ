# Voice Prompt — Prompt Module

> Version: 1.1 | Owner: Islamic Kids Studio AI System | Last Updated: 2026-07-30

---

# VOICE PROMPT — Voice & TTS Optimization

## Purpose
Optimizes narration and dialogue for TTS engines and voice recording.

## Inputs
- Script
- Character profiles
- Pronunciation dictionary (`pronunciation_dictionary.json`)
- Voice rules (`VOICE.md`)
- Age group

## Outputs
- TTS-optimized script
- Pronunciation markers
- Emotion notes
- Pause and timing markers
- Voice selection recommendations

## Rules
- Load `pronunciation_dictionary.json` before generating.
- Load `tts_dictionary.json` for engine overrides.
- Mark Islamic terms with pronunciation guides.
- Use short spoken sentences.
- Include emotional direction for each line.
- Specify breathing and pause timing.
- Confirm warm, natural tone.

## Related Files
`VOICE.md`, `LANGUAGE.md`, `STORY.md`
