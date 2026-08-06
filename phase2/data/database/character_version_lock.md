# Character Version Lock — Episode Continuity System

## Version: 1.1

## Purpose
Every episode must lock exact character versions to prevent continuity breaks during future updates.

## Lock Rules

### Format
`CharacterID vX.Y`

### Examples
- `Zayd v2.0`
- `Amira v2.0`
- `Nuri v2.0`
- `Ummi Layla v2.0`
- `Baba Ahmad v2.0`
- `Dada Yusuf v2.0`

### Lock Per Episode
Every `episode_database.json` entry must reference:
```json
{
  "episode_id": "ep_003",
  "character_versions_locked": {
    "Zayd": "v2.0",
    "Amira": "v2.0",
    "Nuri": "v2.0",
    "Ummi Layla": "v2.0"
  },
  "version_lock_applied": true,
  "version_lock_timestamp": "2026-07-30"
}
```

### Update Rule
If a character design is updated to `v1.3`, previous episodes remain locked to `v1.2`. Only new episodes may use `v1.3`.

### Source Reference
- `phase3/knowledge/characters/knowledge_characters.json`
- `phase2/data/database/character_versions.json`
