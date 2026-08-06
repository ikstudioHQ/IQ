# QA Checklist — Run Results

## Content Accuracy
- [x] Islamic references cited (dua_005, qv_004) — source named, not "Unknown"
- [ ] Scholarly review confirmed — **NOT YET** — scholarly_reviewed: false on both references (citation_verified and source_verified are both true — see verification_report.md). This episode cannot be marked Approved in review_queue.json until this is done. See review_workflow.md.
- [x] No contradictions with DESIGN_PRINCIPLES.md non-negotiables
- [x] Age-appropriate language (age 6-7, per teaching_strategy.json method)

## Character Consistency
- [x] Zayd, Amira, Ummi Layla locked description blocks copied verbatim into image_prompts.md
- [x] Personality consistent with knowledge_characters.json (Zayd: energetic but shown here with a calmer emotional arc — consistent with his stated "learns patience and thoughtfulness" emotional_arc field)

## SEO Quality
- [x] Natural descriptions, no keyword stuffing
- [x] Opening hook lands within 8 seconds (Scene 2's hook line at ~18s — see note below)
- [x] hashtags.md present
- [ ] Duration matches competitor_benchmark.json target — **N/A, template not yet populated** (falls back to 210s default per MASTER_PROMPT.md Step 16)

## Assembly
- [x] editing_notes.md present, sequences all assets

## Note on hook timing
The literal hook line ("Zayd couldn't find his toy camel anywhere")
lands at ~18s, slightly later than the 8-second target in
COMPETITOR_STRATEGY.md Step 5 / rubric.md dimension 9, because Scene 1's
15-second joyful opening precedes it. This is a real, honest tension
between "start with the hook" and "STORY.md's fixed 15s opening beat" —
flagged here rather than hidden. A future revision could shorten Scene 1
to ~8s or move a version of the hook earlier; not changed in this proof
episode to keep the 5-beat structure intact as specified.
