---
id: SOURCES_ISLAMIC_BOOKS_CATALOG
version: 1.0
status: production
depends_on: [phase1/docs/governance/review_workflow.md]
last_updated: 2026-07-31
---

# CATALOG.md — Uploaded Islamic Reference Books

This tracks the 27 books/files the creator provided (originally in a
`New folder` under `Desktop/Business/Youtube/Islamic Studio HQ/`), what's
been extracted into the repository's structured data so far, and — this
matters — a real licensing flag on the Quran translation files.

## ⚠️ Licensing flag — read before using the Quran translation files
`clearquran.zip`, `quran-in-english-clearquran-*.zip`, and `_readme.txt`
inside them state the translation (Talal Itani, ClearQuran) is provided
under **Creative Commons Attribution-NonCommercial-NoDerivs**. That
license has two clauses that conflict directly with this project:
- **NonCommercial** — this channel is being built for monetized YouTube
  content. Using this exact translation's wording in monetized episodes
  is outside what the license permits.
- **NoDerivs** — the license doesn't permit paraphrasing/simplifying the
  translation for children, which is exactly what `MASTER_PROMPT.md`
  requires every Quran reference to do (`translation_simplified` field).

**Do not extract wording from the ClearQuran files into
`quran_verses.json`.** For Quran translations going forward, use a
public-domain or explicitly permissive translation (e.g. Saheeh
International's is commonly distributed for free reproduction, but
verify the specific edition's terms before use — don't assume) or, as
done for `qv_004`/`qv_005` below, cite the verse reference and translate
the meaning independently rather than copying wording from a
restrictively-licensed source. This flag applies to the two `clearquran`
zips and the two `quran-in-english-*` zips; the other 23 files have no
comparable restriction visible in their front matter (most are
free-distribution Islamic dawah booklets, which commonly permit free
reproduction — but that is not a substitute for an actual license check
per book before large-scale extraction; see `review_workflow.md`).

## Extraction status

| File | Format | Extracted into repo? | Notes |
|---|---|---|---|
| `en_Hisn_El_Muslim.pdf` | PDF (scanned, OCR'd) | ✅ Partial — `dua_005` (Hasbunallah dua) and `qv_004` (Aal-e-Imran 3:159, cited via this book's footnote) extracted | 156 pages, only pages ~53-65 (consultation dua, tawakkul dua, morning/evening remembrance) OCR'd so far. Full table of contents captured — see below. Significant remaining extraction opportunity: waking/sleeping/home/mosque/travel duas (items 1-33, 68-132 per TOC) not yet pulled in. |
| `Stories Of The Prophets By Ibn Kathir.pdf` | PDF (real text layer, no OCR needed) | ✅ Partial — Prophet Yunus fully extracted (`prophet_yunus`, `dua_006`, `qv_005`) | Has a real text layer (`pdftotext` works cleanly). Full book covers many more prophets (Adam, Nuh, Ibrahim already partially in repo, plus many not yet added — Musa, Isa, Yusuf, etc.). High-value next extraction target. |
| `clearquran.zip` / `quran-in-english-clearquran-*.zip` | docx/txt | ❌ Not extracted | See licensing flag above — do not extract wording, reference only. |
| `quran-verse-by-verse-text.zip` | txt (per-verse files) | ❌ Not checked for license | Check `_readme.txt` inside before use — same family as ClearQuran, verify separately. |
| `QuranInfo.xlsx` | Spreadsheet | ❌ Not extracted | Likely surah/verse metadata (names, revelation order, verse counts) — low copyright risk (factual metadata), good candidate for populating a future reference table (not yet created) alongside `quran_verses.json`. |
| `en-p-al-arba3un-alnawawiia-abo-zakaria-annawawy-ppp.pdf` (40 Hadith of An-Nawawi) | PDF | ❌ Not extracted | Extremely well-known, commonly free-to-distribute hadith collection — high value for `hadith.json` expansion (currently only 4 entries). |
| `en_The_Description_of_the_Prophet_Prayer.pdf`, `en_Prophet_Muhammads_Manner_of_performing_prayers.pdf` | PDF | ❌ Not extracted | Relevant to a future `t_salah_intro` topic (already in `future_topics.json`). |
| `en-concise-biography.pdf` | PDF | ❌ Not extracted | Seerah (life of the Prophet) material — relevant to future character/story content, not yet a curriculum topic. |
| `en_A_Day_in_the_House_of_the_Messenger_of_Allah.pdf` | PDF | ❌ Not extracted | Good source for "A Day in the Life" style episode content — everyday-manners angle. |
| Remaining 15 files (`Allah Governance on Earth.pdf`, `en-acts-of-hearts-in-hajj-and-umrah.pdf`, `en-glimpse-into-the-islamic-creed.pdf`, `en-correction-of-er-wah.pdf`, `en-atasdid.pdf`, `en-muhammad-in-the-old-testament.pdf`, `risala_en_sifat_alomrah_harmain.pdf`, `en_useful_way_of_leading_happy_life.pdf`, `en-ponder-and-reflect.pdf`, `en-have-you-asked-yourself.pdf`, `en-daea-walrruqyt-alshareia.pdf`, `this is my lord prepared by khaled al khelaiwi.pdf`) | PDF | ❌ Not reviewed yet | Not yet assessed for relevance/extraction — mostly adult-oriented creed/theology texts (Hajj, Umrah rulings, aqeedah). Lower priority for a 2-8 children's curriculum than the prophets/duas/hadith sources above; revisit if/when curriculum expands into older-child (8+) or parent-facing content. |

## Extraction principle going forward
Every new entry added to `phase2/data/islamic/*.json` from these books
must carry `"primary_source"` naming the actual file (not "Unknown
source reference," which the original seed data used) and, where
practical, a page or chapter reference — see `dua_005`, `dua_006`,
`qv_004`, `qv_005`, and `prophet_yunus` for the pattern. This does not
replace human scholarly review (`human_reviewed` stays `false` until
that happens) — it just means the AI-cited source is a real, named,
checkable book instead of an unlabeled claim.

## Related Files
`phase1/docs/governance/review_workflow.md`,
`phase2/data/islamic/*.json`, `MULTI_CHANNEL.md`
