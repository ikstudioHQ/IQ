# MEMORY SYSTEM — AI Memory Design

## Purpose
Defines how the AI remembers previous episodes, lessons, character growth, and repository state.

## Memory Components
- `current_state.json`: Active series, season, episode, topic, age target.
- `last_episode.json`: Previous episode details.
- `learning_progress.json`: Age group, completed topics, current series, progress percentage.
- `generation_log.json`: All previous generations with quality scores.
- `topic_graph.json`: Topic relationships and prerequisites.
- `asset_registry.json`: Used assets.
- `character_relationships.json`: Character dynamics.
- `character_versions.json`: Character design versions.
- `completed_topics.json`: Completed curriculum topics.
- `available_topics.json`: Active topics.
- `future_topics.json`: Planned topics.

## Memory Rules
- Load all memory files before generation.
- Confirm previous episode reference.
- Confirm curriculum progress.
- Confirm topic history to avoid duplication.
- Confirm asset reuse.
- Confirm character consistency.
- Confirm repository version.

## Related Files
`MASTER.md`, `MEMORY.md` (Phase 1), all Phase 2 database files
