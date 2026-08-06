# QA CHECKLIST — Quality Assurance Checklist

## Story Quality
- [ ] Teaches one clear value
- [ ] Gentle conflict
- [ ] Earned resolution
- [ ] Consistent characters
- [ ] Natural writing (not AI-like)
- [ ] No filler or repetition

## Writing Quality
- [ ] Every sentence adds value
- [ ] Conversational English
- [ ] Short spoken sentences
- [ ] Emotional storytelling
- [ ] Show, don't tell

## Islamic Quality
- [ ] Accurate references
- [ ] No invented hadith
- [ ] No invented Quran citations
- [ ] Child-friendly explanations
- [ ] No disputed opinions as facts

## Brand Quality
- [ ] Brand colors and style
- [ ] Consistent characters
- [ ] Warm, safe, cute tone
- [ ] Merchandise-friendly

## SEO Quality
- [ ] Natural descriptions
- [ ] No keyword stuffing
- [ ] Clean metadata
- [ ] Brand references
- [ ] Opening hook lands within 8 seconds (see `phase1/docs/seo/COMPETITOR_STRATEGY.md` Step 5)
- [ ] Duration matches `competitor_benchmark.json` target if populated, else 210 sec default
- [ ] `hashtags.md` present and non-misleading
- [ ] `lyrics_and_song.md` present, structured with [Verse]/[Chorus] tags, age-appropriate vocabulary, ready to feed to an audio/song generation tool with no manual editing
- [ ] `verification_report.md` present — every Islamic claim has a source_id, no unexplained "Claims without a direct citation" or unresolved "Warnings" sections (see verification_pipeline.md — checkable without Islamic domain knowledge)
- [ ] `image_prompts.md` and `animation_directions.md` blocks are self-contained (locked character description inlined, not referenced) — verify by spot-checking one block requires zero repo lookup to use

## Voice Quality
- [ ] Natural narration
- [ ] Proper pronunciation
- [ ] Warm tone
- [ ] Child-appropriate pace

## Assembly
- [ ] `editing_notes.md` present and sequences all assets into an edit timeline

## Validation
Every item must be confirmed PASS before packaging. Log all results in `generation_log.json`.

## Related Files
`phase1/docs/rules/RULES.md`, `phase1/docs/master/MASTER.md`, `phase1/docs/brand/BRAND.md`, `phase1/docs/story/STORY.md`, `phase1/docs/islamic/ISLAMIC.md`, `phase1/docs/seo/COMPETITOR_STRATEGY.md`
