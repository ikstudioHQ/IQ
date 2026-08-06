# Missing Knowledge Report — Fairness Regression Run (v2.15)

execution_mode: blocked
production_ready: false
repository_status: REPOSITORY_VERIFIED (v2.14 at time of this run's preflight check)

## Requested episode
"The Day Zayd and Amira Disagreed Over Sharing Their Favorite Toy and
Learned Fairness" — Age 5-7, English, 8-10 min requested, Execution
Mode: Auto. This is the mandated P2-28 regression run, executed against
the real repository (confirmed via `tools/preflight_check.py` →
REPOSITORY_VERIFIED before any other step ran).

## Preflight result
```
$ python3 tools/preflight_check.py .
STATUS: REPOSITORY_VERIFIED
  version: 2.14
  fingerprint: repository_manifest.json:2.14|knowledge_index.json:2.14|islamic_file_count:8|character_file_count:6
```
Repository presence and identity confirmed real before proceeding —
per execution_modes.md's Repository Presence Guard (v2.15). This run
does NOT repeat the Document 7 failure: nothing below was invented from
model memory; every gap is a real, checked absence in the actual
`phase3/knowledge/concepts/*.json` files.

## Smart Fallback trace (real, not simulated)
| Concept candidate | related_quran | related_hadith | related_duas | related_prophets | Verdict |
|---|---|---|---|---|---|
| concept_justice (Adl — closest thematic match; its own age-4 definition is literally "Taking turns fairly") | [] | [] | [] | [] | No citable religious evidence at all |
| concept_generosity | [] | [] | [] | [] | No citable religious evidence at all |
| concept_self_control | [] | ['hd_002'] | [] | [] | hd_002 is "speak good or remain silent" — a speech-conduct hadith. Applying it to a sharing/fairness claim would be UNSUPPORTED or at best a heavy INTERPRETIVE stretch (per verification_pipeline.md's new Semantic Claim Support levels) — not a genuine adjacent match. |
| concept_honesty | [] | ['hd_002'] | [] | [] | Same hd_002 issue; honesty (truth-telling) is not the same concept as fairness (equitable sharing) regardless. |

**No concept in the repository has real Quran/Hadith/Dua/Prophet
evidence (`citation_verified: true`) that genuinely supports a
fairness-in-sharing story.** Per `execution_modes.md`'s Smart Fallback
bar ("at least a concept definition plus one Quran/hadith/dua/prophet
reference with citation_verified: true"), this fails the bar.

## Result: BLOCKED
```
execution_mode: BLOCKED
reason: Smart Fallback found no concept with sufficient real evidence
        for a genuine fairness/sharing story.
```
No episode files were generated. No characters were invented. No
Quran/Hadith was recalled from model memory and substituted for
repository evidence. This is the correct, honest outcome — not a
failure of this run, but confirmation that the repository's own
knowledge base doesn't yet cover this topic, which is now visible and
actionable instead of papered over.

| Missing Item | Reason | Repository Location | Files to Update | Estimated Fix Effort | Priority |
|---|---|---|---|---|---|
| Quran/Hadith/Dua evidence for 'adl (fairness/justice in sharing) | concept_justice exists but is entirely uncited | phase2/data/islamic/quran_verses.json, hadith.json | Both files + concept_justice.json's related_* arrays | ~30-45 min — An-Nahl 16:90 ("Allah commands justice and good conduct") is a strong, well-known real candidate; needs real extraction per knowledge_builder_pipeline.md, not assumed from memory | Critical |
| concept_justice fully unlinked (0 related items in every category after this run's mislink fix) | vocab_018 was incorrectly linked (Masjid, unrelated) and has been removed as a real bug fix this run — concept now has zero links of any kind | phase3/knowledge/concepts/concept_justice.json | Same file | ~15 min once real evidence exists above | High |
| No conflict specifically modeling "two children want the same toy at once" | conflict_library.json's justice-adjacent entries (cf_003, "broken promise") don't match a simultaneous-sharing scenario | phase3/knowledge/story/conflict_library.json | Same file | ~10 min | Medium |
