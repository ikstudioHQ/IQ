---
id: COMMUNITY_MODERATION
version: 1.0
status: production
depends_on: [phase1/docs/governance/review_workflow.md]
last_updated: 2026-08-01
---

# MODERATION.md — Comment Moderation Policy

A children's Islamic channel draws two specific comment risks beyond
normal YouTube moderation: sectarian/theological arguments in the
comments, and adults specifically targeting content aimed at children.
Both need a plan before the channel has an audience, not after.

## Auto-hide / auto-flag categories (set in YouTube Studio, not this repo)
- Slurs or hate speech (standard YouTube filter — enable "Hold potentially
  inappropriate comments for review").
- Sectarian-dispute trigger words (madhab names paired with dismissive
  language, "bid'ah," "kafir," "haram" used as an attack rather than a
  question) — hold for manual review, don't auto-delete (a genuine
  question shouldn't be silently removed).
- Any comment directed at a child by username/behavior pattern rather
  than at the content — escalate immediately, don't just hide (see
  "Child-targeting" below).
- Off-platform contact attempts ("DM me," "check my channel" spam) —
  standard spam filter.

## Response templates (for the creator, not auto-posted)
- **Theological dispute in comments** ("that's not authentic," "that's
  the wrong school of thought"): Don't argue in the replies. Short,
  calm reply: *"Jazakallahu khair for raising this — we always welcome
  a qualified scholar's correction. We'll look into the source."* Then
  actually route it through `phase1/docs/governance/dispute_response.md`
  — see that file for what happens next.
- **Disagreement about content style/language choices** (not
  theological): Thank them, note it, don't over-explain in public.
- **Genuine child-safety concern raised by a parent**: Respond promptly
  and take it seriously — these are worth escalating even if they turn
  out to be a false alarm.

## Child-targeting — escalate, don't just moderate
If a comment or account pattern suggests an adult specifically targeting
child viewers (not just spam — actual grooming-pattern behavior:
soliciting contact, inappropriate compliments toward the children shown
in the videos, requests to "talk privately"): report the account to
YouTube immediately via their child-safety reporting flow, disable
replies on that comment thread if needed, and do not attempt to
"handle" it purely through normal comment moderation. This is a
platform-safety issue, not a customer-service one.

## What this file does not cover
Actual comment-filtering keyword lists, YouTube Studio configuration
steps, and platform-specific reporting flows change over time — check
YouTube's current Creator Studio documentation directly rather than
relying on a static list here going stale.

## Related Files
`phase1/docs/governance/dispute_response.md`,
`phase1/docs/community/PARENT_TRUST_PAGE.md`
