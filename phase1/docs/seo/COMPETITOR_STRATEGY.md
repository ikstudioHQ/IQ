---
id: SEO_COMPETITOR_STRATEGY
version: 1.0
status: production
depends_on: [SEO.md, BRAND.md, DESIGN_PRINCIPLES.md]
used_by: [AI Pipeline, Content Generator, Channel Growth]
last_updated: 2026-07-30
---

# COMPETITOR_STRATEGY.md — Getting Recommended Alongside a Target Competitor

## Purpose
Defines how Islamic Kids Studio content should be built, tagged, and
formatted so YouTube's recommendation system treats it as a close match to
a named target competitor — the same mechanism that let that competitor
grow fast in ~40 days. This file does not replace `SEO.md`; it adds the
specific "get recommended next to X" layer on top of it.

## How YouTube's Suggested/Recommended System Actually Works (plain terms)
YouTube doesn't recommend videos because they share tags. It recommends
videos that **co-view well** — meaning a meaningful percentage of people who
watch Video A also watch Video B in the same session, and B keeps them
watching. Three things drive that:
1. **Same format signature** — similar length, similar pacing, similar
   thumbnail style, similar title structure. The algorithm clusters by
   viewing pattern, and format is the strongest predictor of it.
2. **Same audience retention curve** — if your video holds attention as
   well as the competitor's in the first 30 seconds and across the full
   watch, it gets treated as substitutable/complementary content for that
   same audience.
3. **Topical and semantic closeness** — same subject matter, overlapping
   search terms, overlapping "watched next" behavior from real viewers.

You cannot force placement. You can maximize the odds by removing every
reason the algorithm would treat your video as a *different* kind of
content than the competitor's.

## Step 1 — Study the Target Competitor Before Every Batch of Episodes
Before generating a new batch of episodes, the creator (not the AI) should
manually pull the competitor's last 10-15 videos and record:
- Average video length (to the second, if possible).
- Title pattern (word count, whether it's a question, whether it names the
  character, whether it states the lesson).
- Thumbnail pattern (close-up face vs. wide scene, text on thumbnail or
  not, color saturation, number of characters shown).
- Upload frequency and day/time.
- Which of their videos have the highest view counts, and what those
  specific videos have in common (topic, length, thumbnail).
- Their top 5-10 tags/keywords, pulled from a tag-viewer tool or from the
  video description itself.

Log this in `phase2/data/database/competitor_benchmark.json` (create/update
this file every time you refresh the research — see schema below). The
Master Prompt pipeline reads this file at Step 16 (Plan Episode) when a
`Profile: YouTube` generation is requested, and adjusts duration/format
recommendations to stay close to the competitor's proven pattern rather
than only using the repository's own defaults.

### `competitor_benchmark.json` schema
```json
{
  "schema_version": "1.0",
  "updated_at": "<date>",
  "competitor_channel_name": "<name>",
  "benchmark_videos": [
    {
      "title": "<their title>",
      "length_seconds": 0,
      "view_count_at_capture": 0,
      "thumbnail_style": "<close-up face / wide scene / text overlay / no text>",
      "published_at": "<date>",
      "notes": "<why this one performed well>"
    }
  ],
  "average_length_seconds": 0,
  "common_title_pattern": "<e.g. '[Character] Learns [Value] | Islamic Story for Kids'>",
  "common_tags": ["...", "..."],
  "upload_days_observed": ["..."]
}
```

## Step 2 — Match Format, Not Just Topic
Once `competitor_benchmark.json` exists, every new episode should target:
- **Duration within ±15% of the competitor's average length**, not just
  the repository's default 210 seconds. If the competitor's best-performing
  videos run 4-5 minutes, `MASTER_PROMPT.md`'s `Duration Target` input
  should default toward that range for this channel, not toward whatever
  the repo template originally assumed.
- **A title structure that mirrors theirs syntactically** (not their exact
  words — see `SEO.md`'s no-keyword-stuffing rule, which still applies).
  If they consistently use `"[Character] Learns [Value] — Islamic Story for
  Kids"`, Islamic Kids Studio titles should follow an equally consistent,
  recognizable pattern of our own — e.g. `"Zayd and Amira Learn [Value] |
  Islamic Kids Studio"`. Consistency itself is a signal; a channel with 20
  videos that all look format-matched to a genre reads as "more of the
  same good thing" to the recommendation system.
- **A thumbnail composition that matches the competitor's proven style**
  (close-up character face with big expressive eyes, warm background,
  minimal or no text overlay, consistent character positioning) —
  `thumbnail_prompt.md` and `thumbnail.md` should pull the composition
  style from `competitor_benchmark.json` rather than only from `BRAND.md`.

## Step 3 — Playlist and End-Screen Adjacency
Recommendation weight comes heavily from **sessions**, not single videos.
- Build playlists that mirror the competitor's playlist structure (e.g. a
  "Good Manners" series, a "Prophet Stories" series, a "Duas for Kids"
  series) so a viewer who finishes one episode has an immediate next
  episode from the same playlist queued.
- Use end screens and cards to link to the next episode in the same
  series, not to unrelated content — this keeps session-length and
  co-watch data clean and topic-consistent, which is what the algorithm
  rewards.
- Upload on a fixed, predictable schedule (`settings.yaml` already states
  weekly — keep this fixed once a schedule is chosen; irregular cadence
  measurably hurts suggested-video placement for young/growing channels).

## Step 4 — Overlap Keywords Without Copying Them
Pull the competitor's most-used tags/keywords from
`competitor_benchmark.json` and cross-reference them against
`phase2/data/seo/keyword_database.csv`. Any keyword that's relevant to both
the competitor's proven audience and this channel's actual content should
be added to `keyword_database.csv` (if not already present) so
`seo_prompt.md`/`tags.md` naturally draw from it. Do not copy their exact
titles, descriptions, or thumbnail text — that risks a duplicate-content or
misleading-metadata flag and won't out-compete the original for its own
search terms anyway. The goal is semantic neighborhood, not duplication.

## Step 5 — First 30 Seconds Discipline
Because retention curve is the single strongest recommendation signal,
every episode's **opening 15-30 seconds** (the `STORY.md` "Opening" beat)
should be reviewed specifically against the competitor's opening pattern:
does their video show the main character and establish the emotional hook
within the first 5-8 seconds? Match that discipline. `qa_checklist.md`
should include an explicit item: "Opening hook lands within 8 seconds,
matching or beating competitor benchmark" — add this to
`phase4/engine/checklists/qa_checklist.md` (see change list below).

## What This Cannot Do
This document optimizes the *inputs* the algorithm rewards. It cannot
guarantee placement — no legitimate method can, and any tool or "trick"
claiming to force suggested placement (artificial engagement, misleading
titles/thumbnails, watch-time padding) violates YouTube's policies and
risks the channel entirely. The realistic target from this approach is
**meaningfully improved odds of co-recommendation over 10-20 consistent,
format-matched episodes** — not a guarantee on episode one.

## Related Files
`phase1/docs/seo/SEO.md`, `phase1/docs/brand/BRAND.md`,
`phase4/engine/prompts/seo_prompt.md`,
`phase4/engine/prompts/thumbnail_prompt.md`,
`phase2/data/database/competitor_benchmark.json` (create on first use),
`phase2/data/seo/keyword_database.csv`

references:
- SEO_001
- BRAND_001
- COMPETITOR_STRATEGY_001
