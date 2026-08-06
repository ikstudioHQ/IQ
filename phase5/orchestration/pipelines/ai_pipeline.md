# AI PIPELINE — Complete Pipeline Definition

## Purpose
Defines the complete AI pipeline from user request to final packaged episode.

## Pipeline Flow
1. User Request
2. Load Config (`settings.yaml`, `ai_models.yaml`)
3. Load Knowledge (`ISLAMIC.md`, `STORY.md`, `CHARACTER.md`, `WORLD.md`, `CURRICULUM.md`)
4. Load Rules (`RULES.md`)
5. Load Character Files (`knowledge_characters.json`)
6. Load World Files (`knowledge_world.json`)
7. Load Curriculum (`knowledge_curriculum.json`)
8. Load Islamic Knowledge (`islamic/*.json`)
9. Load Pronunciation Dictionary (`pronunciation_dictionary.json`)
10. Load Databases (`phase2/data/database/*.json`)
11. Planner
12. Duplicate Checker (`available_topics.json` + `completed_topics.json`)
13. Curriculum Checker (`knowledge_curriculum.json` + `learning_progress.json`)
14. Story Generator (`story_prompt.md` + `story_template.md`)
15. Dialogue Generator (`script_prompt.md` + `dialogue_rules.md`)
16. SEO Generator (`seo_prompt.md` + `seo/*.md`)
17. Thumbnail Generator (`thumbnail_prompt.md` + `thumbnail_template.md`)
18. Voice Generator (`voice_prompt.md` + `voice/*.md`)
19. QA Validation (`qa_checklist.md` + `qa_prompt.md`)
20. Package Episode
21. Update Database (`current_state.json`, `last_episode.json`, `generation_log.json`, `episode_database.json`)
22. Save Package Locally
23. Generate ZIP

## Brand Integration
Every pipeline step must confirm:
- Brand: Islamic Kids Studio / @IslamicKidsHQ
- Logo text: Islamic Kids Studio
- Watermark: IK Studio
- Keywords: Islamic Kids, Islamic Stories, Muslim Kids, Quran for Kids, Dua for Kids, Islamic Cartoons, Islamic Learning, Ramadan for Kids, Eid for Kids, Arabic for Kids

## Related Files
`MASTER.md`, `WORKFLOW.md`, `MEMORY.md`
