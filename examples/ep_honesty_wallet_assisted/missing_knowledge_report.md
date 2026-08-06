# Missing Knowledge Report — ep_honesty_wallet_assisted

execution_mode: assisted
production_ready: false
version: v2.14

Original request: "The Day Zayd Found a Lost Wallet and Learned Why
Honesty Pleases Allah" (8-10 min). Smart Fallback (execution_modes.md)
found `concept_honesty` has enough real evidence (vocab_005, vocab_006,
qv_004, dua_005 — all citation_verified: true) to generate a genuine,
narrower story, so this run produced "The Day Zayd Chose to Be Honest"
in ASSISTED mode instead of blocking outright.

| Missing Item | Reason | Repository Location | Files to Update | Estimated Fix Effort | Priority |
|---|---|---|---|---|---|
| Hadith/ruling on returning lost property (luqatah) | 0 matches repo-wide across hadith.json, quran_verses.json, good_manners.json | phase2/data/islamic/hadith.json | hadith.json (+ knowledge_index.json if a new category is warranted) | ~30 min — extract from en-p-al-arba3un-alnawawiia-abo-zakaria-annawawy-ppp.pdf (40 Hadith an-Nawawi, already catalogued, unextracted per sources/islamic_books/CATALOG.md) | Critical |
| Sourced evidence for "honesty pleases Allah" as a general claim | No Quran verse on truthfulness exists; hd_002 (speak good or remain silent) covers speech, not property honesty, and would be a stretch to carry this specific claim | phase2/data/islamic/quran_verses.json, hadith.json | Both files | ~30 min — same source book likely covers this alongside luqatah material | Critical |
| Sourced evidence for "Allah rewards returning what isn't yours" | No entry supports this specific reward-framing; qv_004 supports trusting Allah after deciding, not a reward claim for this specific act | phase2/data/islamic/quran_verses.json, hadith.json | Both files | ~20 min once the above two items are sourced from the same material | High |
| Curriculum topic node for honesty (t_honesty) | concept_honesty exists (phase3/knowledge/concepts/) but no matching node in available_topics.json/topic_graph.json | phase2/data/database/available_topics.json, phase2/data/database/topic_graph.json | Both files | ~10 min — concept package already has recommended_age_range and a recommended_default combination to draw from | Medium |
| Story conflict specifically about a found/lost item of value (not a promise or a toy) | conflict_library.json's honesty-tagged conflicts (cf_003, cf_006, cf_011, cf_014, cf_017, cf_018) cover promises, sharing, and shop items, not a found valuable item scenario | phase3/knowledge/story/conflict_library.json | conflict_library.json | ~10 min | Low — cf_014 ("wanting a toy that isn't yours at a store") is close enough that this episode reused its spirit rather than blocking on it |

## What was generated instead
See episode_summary.md and verification_report.md — a narrower, fully
real-evidence-backed story using only vocab_005, vocab_006, qv_004, and
dua_005, with the wallet-finding situation kept (it's a valid, relatable
conflict) but no specific ruling or reward-claim attached to it.

## Repository state confirmed at generation time
- hadith.json: 4 entries (hd_001-hd_004), none concern property.
- quran_verses.json: 5 entries (qv_001-qv_005), none concern honesty/property.
- good_manners.json: 8 entries (mann_001-mann_008), none cover found property.
- Repo-wide sweep for "lost property / luqat / wallet / found money / lost item": 0 matches.
