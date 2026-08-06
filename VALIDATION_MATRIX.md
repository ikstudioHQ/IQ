# Validation Matrix — Reusable Quality Framework

## Version: 1.1

## Purpose
Centralized validation rules used by QA prompts, review prompts, and the Master Prompt.

## Validation Categories

### Story Quality
- [PASS/FAIL] One clear value taught.
- [PASS/FAIL] Gentle conflict.
- [PASS/FAIL] Earned resolution.
- [PASS/FAIL] Consistent characters.
- [PASS/FAIL] Natural writing.
- [PASS/FAIL] Every sentence contributes.
- [PASS/FAIL] No filler/repetition/robotic language.

### Writing Quality
- [PASS/FAIL] Conversational English.
- [PASS/FAIL] Short spoken sentences.
- [PASS/FAIL] Emotional storytelling.
- [PASS/FAIL] Show, don't tell.
- [PASS/FAIL] Consistent personalities.

### Islamic Quality
- [PASS/FAIL] Accurate references (verified sources only).
- [PASS/FAIL] No invented hadith.
- [PASS/FAIL] No invented Quran citations.
- [PASS/FAIL] No disputed opinions as facts.
- [PASS/FAIL] Child-friendly explanations.

### Brand Quality
- [PASS/FAIL] Warm pastel palette.
- [PASS/FAIL] Soft rounded shapes.
- [PASS/FAIL] Large expressive eyes.
- [PASS/FAIL] Child-scale.
- [PASS/FAIL] Merchandise-friendly.

### Curriculum Quality
- [PASS/FAIL] Age-appropriate.
- [PASS/FAIL] Prerequisites met.
- [PASS/FAIL] One concept per episode.
- [PASS/FAIL] Learning objective clear.

### Technical Quality
- [PASS/FAIL] All JSON valid.
- [PASS/FAIL] All YAML valid.
- [PASS/FAIL] All references verified.
- [PASS/FAIL] No broken links.
- [PASS/FAIL] No placeholders.

### Voice & Language Quality
- [PASS/FAIL] Pronunciation dictionary loaded for Islamic terms.
- [PASS/FAIL] Child-friendly pronunciation guides.
- [PASS/FAIL] TTS overrides present.
- [PASS/FAIL] No forbidden pronunciations.

## Usage
Every prompt (`qa_prompt.md`, `review_prompt.md`, `MASTER_PROMPT.md`) references this matrix. Confirm all applicable categories pass before final output.
