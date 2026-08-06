---
id: VOICE_VOICE
version: 1.1
status: production
depends_on: [MASTER.md, BRAND.md]
used_by: [AI Pipeline, Content Generator]
last_updated: 2026-07-30
---

# VOICE — Narration & TTS System

## Purpose
Defines voice requirements, TTS optimization, pronunciation integration.

## Requirements
Conversational English, short spoken sentences, emotional warmth, child-appropriate pace, parent-engaging tone, proper breathing, TTS engine compatibility.

## AI Instructions
Load pronunciation dictionary before generating voice content. Load tts_dictionary.json for engine overrides.

## Best Practices
Always load `pronunciation_dictionary.json` before generating voice content. Confirm pronunciation consistency across episodes. Confirm emotional warmth and child-appropriate pace in every output.

## Future Expansion
Voice system will expand with multi-language TTS, parent podcast narration, and merchandise audio guides.

## Related Files
LANGUAGE.md, STORY.md, SEO.md
