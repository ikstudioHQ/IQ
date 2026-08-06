---
id: GOVERNANCE_DISPUTE_RESPONSE
version: 1.0
status: production
depends_on: [phase1/docs/governance/review_workflow.md]
last_updated: 2026-08-01
---

# dispute_response.md — When a Published Episode Gets Theologically Challenged

Different from `MODERATION.md` (that's comment-level noise). This is for
when a specific episode's content gets a real, specific challenge — a
hadith authenticity question, a fiqh ruling called disputed between
schools, a translation accuracy concern — raised publicly (comments,
social media, or directly by a viewer/scholar).

## Procedure
1. **Don't argue publicly in real time.** Acknowledge receipt calmly
   (see `MODERATION.md`'s response template) and take the specifics
   offline/to review, even if you're confident the challenge is wrong.
2. **Identify the exact entry.** Find the `dua_id`/`hadith_id`/`verse_id`/
   `prophet_id` in `phase2/data/islamic/*.json` that the episode cited —
   `episode_database.json`'s `character_versions_locked`-style record
   (or the episode's own generation log) should trace back to the exact
   `primary_source` field used.
3. **Check `scholarly_reviewed` status.** If `false` (the current default
   for all 37 entries as of v2.6 — see `REPO_HEALTH_REPORT.md`), this is
   exactly the scenario `review_workflow.md` warned about: an AI-cited
   source hasn't had independent human confirmation yet. Route to a
   qualified reviewer now, treat the challenge as plausible until they
   confirm either way.
4. **If the reviewer confirms the entry was correct:** respond with the
   specific citation and source, calmly, once — don't escalate into a
   prolonged public debate. Update `scholarly_reviewed: true` on that entry
   per `review_workflow.md`.
5. **If the reviewer finds the entry was wrong or disputed:** correct it
   per `deprecation_policy.md`'s per-item versioning convention (bump
   `version`, add a `change_note`), log it honestly in `CHANGELOG.md`
   per `change_log_policy.md` (no minimizing language), and consider
   whether the published episode needs a pinned-comment correction or
   video update, case by case.
6. **If the dispute is a genuine scholarly difference of opinion**
   (different madhabs, not a factual error): this isn't a "fix" — note
   in the entry's metadata that it reflects one accepted position among
   others, per `DESIGN_PRINCIPLES.md`'s non-negotiable on disputed
   opinions never being presented as the only view. Update the episode's
   description or a pinned comment to note the same, if relevant.

## Why this matters more here than for a general content channel
Religious content aimed at children carries higher trust stakes than
average — a visible, well-handled correction builds more long-term trust
than a defensive non-response, and a defensive non-response to a real
error is a much bigger reputational risk here than for most content
categories.

## Related Files
`phase1/docs/governance/review_workflow.md`,
`phase1/docs/governance/deprecation_policy.md`,
`phase1/docs/governance/change_log_policy.md`,
`phase1/docs/community/MODERATION.md`
