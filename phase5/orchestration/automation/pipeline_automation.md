# PIPELINE AUTOMATION — Automation Design

## Purpose
Defines how automation connects all repository components.

## Automation Principles
- Fully automated from user request to package.
- Modular — each step is independent.
- Scalable — supports thousands of episodes.
- Maintainable — easy to update rules and templates.
- AI-friendly — every document is readable by AI.
- Human-readable — easy for humans to maintain.

## Automation Components
1. Config loader (`settings.yaml`, `ai_models.yaml`)
2. Knowledge loader (`MASTER.md`, `BRAND.md`, domain docs)
3. Memory loader (`current_state.json`, `last_episode.json`, etc.)
4. Planner (topic selection, curriculum check)
5. Generator modules (story, dialogue, SEO, thumbnail, voice)
6. Validation module (`qa_checklist.md`, `review_checklist.md`)
7. Packaging module (ZIP creation, file organization)
8. Database updater (all Phase 2 database files)
9. Update module (local tracking, changelog update)
10. Delivery module (ZIP return, confirmation)

## Related Files
`MASTER.md`, `WORKFLOW.md`, `MEMORY.md`
