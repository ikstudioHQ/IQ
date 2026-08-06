# examples/ — Proof the Pipeline Runs, All Three Execution Modes

As of v2.14, `MASTER_PROMPT.md` Step 14 no longer just PASS/STOPs on
missing Islamic evidence — it determines one of three execution modes
(`phase5/orchestration/planning/execution_modes.md`). This folder has a
real, generated example of each.

## 🟢 `ep_tawakkul_lost_toy/` — PRODUCTION MODE
All required evidence for "trust in Allah" was real, named, and
content-checked (`citation_verified`/`source_verified` both true). Full
28-file package generated normally. `execution_mode: production` is
tagged in its `validation_report.md`. Note: `production_ready: true`
here means the *evidence* is complete — it's still not `approved` in
`review_queue.json`, because `scholarly_reviewed` is `false` on its
sources. Those are two different, intentionally separate gates — see
`verification_pipeline.md`.

## 🟡 `ep_honesty_wallet_assisted/` — ASSISTED MODE
Requested: *"The Day Zayd Found a Lost Wallet and Learned Why Honesty
Pleases Allah"* (8-10 min). The repository had zero evidence for a
lost-property ruling or an "Allah rewards honesty" claim — confirmed by
direct repo inspection (see the original `missing_knowledge_report.md`
this whole feature was built in response to). Instead of blocking
outright, Smart Fallback found `concept_honesty` had real evidence
(sidq, amanah, a trust-in-Allah verse, a dua) — enough for a genuine,
narrower story: *"The Day Zayd Chose to Be Honest."* Duration was
auto-corrected from 600s to 300s (logged in `episode_summary.md`). Read
`missing_knowledge_report.md` (the extended Missing Item/Reason/
Location/Files/Effort/Priority schema) and
`repository_improvement_suggestions.md` (new file type, ranked
Critical/High/Medium/Low) inside this folder — those two files are what
Assisted Mode adds on top of the normal package.

## 🔴 `ep_blocked_demo/` — BLOCKED MODE
A deliberately constructed request with no real adjacent concept to
fall back to (not a real production topic — built specifically to
exercise this path for the v2.14 validation requirement). Only
`missing_knowledge_report.md` was produced; no episode files, nothing
fabricated. This is meant to be the rare outcome — most gaps that used
to hit v2.13's hard-stop now resolve to Assisted Mode instead, as the
honesty episode demonstrates.

## How these were produced
All three were run through `tools/package_episode.py`, which now
detects execution mode from the files present (a Blocked-mode folder
with only `missing_knowledge_report.md`, an Assisted-mode folder with
that file alongside normal episode files) and adjusts its required-file
checking and messaging accordingly — confirmed working, not just
described, by actually running it against all three folders.

**Do not treat any of these as publishable content as-is.** They exist
to prove the three-mode mechanics work end-to-end, and to give a
concrete reference for what each mode's output should look like.
