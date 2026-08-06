# Subtitle Prompt — Prompt Module

> Version: 1.1 | Owner: Islamic Kids Studio AI System | Last Updated: 2026-07-30

---

# SUBTITLE PROMPT — Subtitle Generation

## Purpose
Generates accurate subtitles with Islamic term accuracy.

## Inputs
- Script
- Pronunciation dictionary
- Language settings (`languages.yaml`)
- TTS overrides

## Outputs
- Subtitle file content (`.srt` format)
- Pronunciation verification notes
- Translation notes for Arabic terms

## Rules
- Ensure Islamic terms match pronunciation dictionary.
- Use child-friendly language.
- Keep lines short (max 42 characters per line for readability).
- Include timing that matches emotional pacing.
- Confirm no spelling errors.

## Multi-Language Subtitles (added v2.7)
`published_videos.json` already declares `subtitle_languages: ["en", "ar"]`
per video, but the pipeline previously only specified English subtitle
generation plus vague "translation notes." This makes Arabic (and
optionally Urdu) an actual required output, not a note:
- **`subtitles_en.srt`** — English, as specified above.
- **`subtitles_ar.srt`** (Arabic) — generate only when
  `phase2/data/config/languages.yaml` marks Arabic `status: active` (it
  is currently `status: planned` — see the note below). When active,
  uses `phase2/data/language/arabic_words.json`'s `arabic_script` field
  for every Islamic term that appears there; for narrative English
  dialogue without an existing Arabic term entry, provide a plain,
  simple Arabic translation of the line (not a literal AI
  back-translation of complex English phrasing — keep it as simple as
  the English original per `CHILD_DEVELOPMENT_MATRIX.md`'s target age
  band).
- **`subtitles_ur.srt`** (Urdu) — optional per episode, generate only
  when `languages.yaml` marks Urdu as active for this channel; large
  Muslim audience reach outside English/Arabic markets makes this a
  reach multiplier, but don't generate a language track nobody's
  confirmed the channel is targeting.
- Same 42-character-per-line and pronunciation-accuracy rules apply to
  every language track, not just English.
- **Known discrepancy, not yet resolved:** `published_videos.json`
  records `subtitle_languages: ["en", "ar"]` on already-published
  episodes (pv_001-pv_003), but `languages.yaml` marks Arabic
  `status: planned`, not `active`. Either those episodes genuinely have
  Arabic subtitles (in which case `languages.yaml` should be updated to
  `status: active`) or the field was set aspirationally and those
  episodes only actually have English (in which case
  `published_videos.json` needs correcting). Resolve which is true
  before generating new Arabic tracks under this spec — don't compound
  the inconsistency with new content until it's confirmed.

## Related Files
`LANGUAGE.md`, `VOICE.md`, `STORY.md`,
`phase2/data/language/arabic_words.json`, `phase2/data/config/languages.yaml`
