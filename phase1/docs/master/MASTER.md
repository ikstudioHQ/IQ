---
id: MASTER_MASTER
version: 1.1
status: production
depends_on: [MASTER.md, BRAND.md]
used_by: [AI Pipeline, Content Generator]
last_updated: 2026-07-30
---

# MASTER — Repository Control Document

## Purpose
Defines repository-level rules, structure, versioning, and AI interaction patterns.

## Overview
MASTER governs all phases. Every file references it. Every AI action begins here.

## Responsibilities
- Repository structure enforcement
- Phase boundary definition
- Brand consistency
- AI instruction routing
- Version tracking

## Design Principles
Modular folders, zero duplication, cross-referenced links, AI-optimized headers.

## AI Instructions
Before generating any episode:
1. Load MASTER.md
2. Load BRAND.md
3. Load CURRICULUM.md and ISLAMIC.md
4. Load STORY.md and CHARACTER.md
5. Confirm all rules in RULES.md

## Rules
- Never generate JSON/YAML/CSV in Phase 1
- Never create copyrighted characters
- Never use filler text
- Never duplicate explanations

## Best Practices
Update MASTER.md when new phases are added.

## Future Expansion
Phase 6: Analytics. Phase 7: Multi-language.

## Related Files
README.md, BRAND.md, CONTENT_STRATEGY.md, RULES.md, CHANGELOG.md


references:
- PHASE_001 (Phase 1 Foundation)
- BRAND_001 (Brand Identity)
- CONTENT_001 (Content Strategy)
- CUR_001 (Curriculum)
- STORY_001 (Story System)
- CHAR_001 (Character Design)
- WORLD_001 (World Design)
- ISLAM_001 (Islamic Knowledge)
- LANG_001 (Language System)
- SEO_001 (SEO Strategy)
- ANIM_001 (Animation)
- VOICE_001 (Voice System)
- RULES_001 (Rules)
- MEMORY_001 (Memory Design)
- TEMPL_001 (Templates)
- PROMPT_001 (Prompt Architecture)
- WORKFLOW_001 (Workflow Design)
- DECISION_001 (Decision Framework)
- ROADMAP_001 (Development Roadmap)
- CHANGELOG_001 (Version History)
