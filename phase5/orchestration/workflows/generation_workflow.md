# GENERATION WORKFLOW — Episode Generation Workflow

## Purpose
Defines the step-by-step workflow for generating one complete episode.

## Workflow Steps
1. Confirm user request (topic, age, series).
2. Load MASTER.md and BRAND.md.
3. Load current memory (`current_state.json`, `last_episode.json`).
4. Confirm no duplicate topic (`available_topics.json` vs `completed_topics.json`).
5. Confirm curriculum prerequisites (`knowledge_curriculum.json` + `topic_graph.json`).
6. Load character profiles (`knowledge_characters.json`).
7. Load world settings (`knowledge_world.json`).
8. Load story rules (`STORY.md`, `RULES.md`).
9. Generate story outline (`story_prompt.md`).
10. Generate script (`script_prompt.md`).
11. Confirm dialogue rules (`dialogue_rules.md`).
12. Confirm narration rules (`narration_rules.md`).
13. Confirm pronunciation (`pronunciation_dictionary.json`).
14. Generate SEO content (`seo_prompt.md`).
15. Generate thumbnail prompt (`thumbnail_prompt.md`).
16. Generate voice script (`voice_prompt.md`).
17. Generate animation instructions (`animation_prompt.md`).
18. Run QA checklist (`qa_checklist.md`).
19. Confirm Islamic accuracy.
20. Confirm brand consistency.
21. Confirm writing quality.
22. Package episode.
23. Update all database files.
24. Log generation.
25. Generate ZIP package.
26. Confirm final package integrity.

## Error Recovery
If any step fails, log in `generation_log.json`, stop pipeline, and return error explanation. Never publish incomplete or incorrect content.

## Related Files
`phase1/docs/master/MASTER.md`, `phase1/docs/memory/MEMORY.md`, `phase5/orchestration/errors/error_recovery.md`
