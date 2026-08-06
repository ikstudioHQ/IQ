---
id: LANGUAGE_LANGUAGE
version: 1.1
status: production
depends_on: [MASTER.md, BRAND.md]
used_by: [AI Pipeline, Content Generator]
last_updated: 2026-07-30
---

# LANGUAGE — Pronunciation & Linguistic System

## Purpose
Defines pronunciation, Islamic terminology handling, TTS optimization.

## System Components (Phase 2-3)
pronunciation_dictionary.json, phoneme_dictionary.json, tts_dictionary.json, arabic_words.json, islamic_names.json, pronunciation_exceptions.json, forbidden_pronunciations.json.

## Requirements Per Word
Canonical spelling, alternatives, child-friendly pronunciation, IPA, TTS override, engine override, meaning, category, difficulty, usage examples.

## Best Practices
Always reference `pronunciation_dictionary.json` and `arabic_words.json` before generating content with Islamic terms. Confirm TTS overrides are loaded. Confirm child-friendly explanations included.

## Future Expansion
Language system will expand with full multi-language dictionaries, dialect variations, and interactive pronunciation guides.

## Related Files
ISLAMIC.md, VOICE.md, SEO.md
