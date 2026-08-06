---
id: ISLAMIC_ISLAMIC
version: 1.1
status: production
depends_on: [MASTER.md, BRAND.md]
used_by: [AI Pipeline, Content Generator]
last_updated: 2026-07-30
---

# ISLAMIC — Knowledge Base Design

## Purpose
Defines Islamic knowledge structure, references, and usage.

## Knowledge Areas
Daily duas, good manners (Akhlaq), respect, Prophets, Companions, Quran references, authentic Hadith, Islamic values, Ramadan, Eid, Hajj, daily sunnah, festivals.

## Design Principles
Reference approved sources. Mark disputed opinions for scholarly review. Child-friendly explanations. Positive tone.

## Rules
- Never invent hadith
- Never invent Quran citations
- Never present disputed opinions as facts
- Always provide source reference or mark for review

## AI Instructions
Always load `arabic_words.json` and `pronunciation_dictionary.json` (Phase 2) before generating religious content.

## Related Files
CURRICULUM.md, STORY.md, LANGUAGE.md


references:
- CUR_001
- STORY_001
- LANG_001
