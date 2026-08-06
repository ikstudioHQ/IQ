# SCRIPT WORKFLOW — Script Generation Pipeline

## Steps
1. Load master prompt (`master_prompt.md`).
2. Confirm request details (topic, age, series).
3. Load story template (`story_template.md`).
4. Load character profiles (`knowledge_characters.json`).
5. Load world settings (`knowledge_world.json`).
6. Load curriculum rules (`knowledge_curriculum.json`).
7. Load Islamic references (`islamic/` data files).
8. Generate story outline.
9. Generate scene descriptions.
10. Generate dialogue using `dialogue_prompt.md`.
11. Generate narration using `narration_rules.md`.
12. Combine into full script.
13. Load `phase4/engine/prompts/script_prompt.md` for format confirmation.
14. Confirm pronunciation using `pronunciation_dictionary.json`.
15. Confirm emotional direction.
16. Run `qa_checklist.md`.
17. Log results in `generation_log.json`.

## Related Files
`MASTER.md`, `STORY.md`, `CHARACTER.md`, `WORLD.md`
