---
id: WORKFLOWS_WORKFLOW
version: 1.1
status: production
depends_on: [MASTER.md, BRAND.md]
used_by: [AI Pipeline, Content Generator]
last_updated: 2026-07-30
---

# WORKFLOW — Pipeline Design

## Purpose
Defines AI pipeline from request to packaged episode (Phase 5).

## Pipeline Steps
Request → Config → Knowledge → Planning → Generation → Validation → Packaging → Update → Commit.

## Detailed Pipeline
1. User Request
2. Load Config (settings.yaml, ai_models.yaml)
3. Load Knowledge (ISLAMIC.md, STORY.md, CHARACTER.md, etc.)
4. Load Rules (RULES.md)
5. Load Character and World files
6. Load Curriculum
7. Load Islamic Knowledge
8. Load Pronunciation Dictionary
9. Load Databases
10. Planner
11. Duplicate Checker
12. Curriculum Checker
13. Story Generator
14. Dialogue Generator
15. SEO Generator
16. Thumbnail Generator
17. Voice Generator
18. QA Validation
19. Package Episode
20. Update Database
21. Save Final Package
22. Generate ZIP (local package only)

## Related Files
MASTER.md, MEMORY.md, DECISION.md
