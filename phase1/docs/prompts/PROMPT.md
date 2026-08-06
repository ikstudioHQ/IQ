---
id: PROMPTS_PROMPT
version: 1.1
status: production
depends_on: [MASTER.md, BRAND.md]
used_by: [AI Pipeline, Content Generator]
last_updated: 2026-07-30
---

# PROMPT — Prompt System Architecture

## Purpose
Defines modular prompt system (Phase 4).

## Modules
master, story, script, dialogue, thumbnail, image, animation, voice, music, seo, metadata, subtitle, qa, review.

## AI Instructions
Load correct prompt module per pipeline step. Never mix prompts. Validate output.

## Best Practices
Always load the correct prompt module for each pipeline step. Modify inputs, not structure. Keep outputs consistent with brand and rules. Confirm validation passes before using output.

## Future Expansion
Prompt system will expand with new modules for multi-language content, interactive stories, parent guides, merchandise descriptions, and analytics reporting.

## Related Files
TEMPLATE.md, WORKFLOW.md
