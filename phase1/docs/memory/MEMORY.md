---
id: MEMORY_MEMORY
version: 1.1
status: production
depends_on: [MASTER.md, BRAND.md]
used_by: [AI Pipeline, Content Generator]
last_updated: 2026-07-30
---

# MEMORY — AI Memory System Design

## Purpose
Defines how AI remembers previous episodes, lessons, character growth, repository state.

## Components (Phase 2)
current_state.json, last_episode.json, learning_progress.json, generation_log.json, topic_graph.json, asset_registry.json, character_relationships.json.

## AI Instructions
Load memory files before generating content. Check completed_topics.json. Reference last_episode.json. Confirm current_state.json.

## Related Files
All Phase 2 database files
