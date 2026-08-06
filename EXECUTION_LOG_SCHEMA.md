# Execution Log Schema — Structured Tracking

## Version: 1.1

Every generation must produce (or update) `execution_log.json`:

```json
{
  "execution_id": "exec_001",
  "timestamp": "2026-07-30T14:00:00+05:30",
  "user_input": {
    "topic": "Morning Dua for Kids",
    "age_group": 3,
    "duration_target": 210,
    "language": "en",
    "profile": "Episode"
  },
  "loaded_modules": {
    "brand": true,
    "rules": true,
    "design_principles": true,
    "knowledge_index": true,
    "characters": true,
    "world": true,
    "curriculum": true,
    "islamic": true,
    "language": true,
    "pronunciation": true,
    "memory": true,
    "current_state": true,
    "last_episode": true,
    "learning_progress": true,
    "topic_graph": true,
    "asset_registry": false,
    "analytics": false,
    "generation_log": true
  },
  "warnings": [],
  "errors": [],
  "validation_status": {
    "story_quality": "PASS",
    "writing_quality": "PASS",
    "islamic_accuracy": "PASS",
    "brand_consistency": "PASS",
    "seo_quality": "PASS",
    "voice_quality": "PASS",
    "animation_quality": "PASS",
    "packaging_quality": "PASS",
    "repository_quality": "PASS"
  },
  "output_summary": {
    "episode_id": "ep_004",
    "episode_title": "Morning Dua for Kids — Starting the Day with Allah",
    "series_id": "daily_duas",
    "season": 1,
    "duration_target": 210,
    "quality_score": 9.5,
    "confidence": "verified",
    "version": "v1.1"
  },
  "continuity_notes": {
    "previous_episode": "ep_003",
    "current_characters": ["char_zayd", "char_amira", "char_nuri"],
    "character_versions": {"Zayd": "v2.0", "Amira": "v2.0", "Nuri": "v2.0"},
    "curriculum_stage": "Age 3 — Daily Duas",
    "islamic_references": ["dua_001", "dua_002"],
    "quran_references": ["qv_001"],
    "hadith_references": []
  }
}
```
