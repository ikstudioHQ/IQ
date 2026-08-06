---
id: PLANNING_KNOWLEDGE_BUILDER_PIPELINE
version: 1.0
status: production
depends_on: [sources/islamic_books/CATALOG.md, phase1/docs/governance/review_workflow.md]
used_by: [Human Maintainers, AI Pipeline]
last_updated: 2026-08-01
---

# knowledge_builder_pipeline.md — Turning a Book Into Structured Data

This is the actual process used to add `dua_005`, `dua_006`, `qv_004`,
`qv_005`, and `prophet_yunus` in `CHANGELOG.md` v2.5 — written up as a
repeatable procedure rather than a one-off. Follow this whenever a new
source book (from `sources/islamic_books/CATALOG.md` or a newly provided
one) gets extracted into `phase2/data/islamic/`.

## Pipeline steps

1. **Check the license first.** Before any extraction — see
   `sources/islamic_books/CATALOG.md`'s licensing flag section for the
   pattern (the ClearQuran NC-ND case). If a book's license restricts
   commercial use or derivatives and this channel is monetized, do not
   extract wording from it; cite the reference and write the meaning
   independently instead, or skip it.
2. **Determine extractability.** Run `pdffonts`/`pdftotext` (see
   `/mnt/skills/public/pdf-reading/SKILL.md` pattern). A real text layer
   → extract directly. No text layer (scanned) → OCR with tesseract,
   page by page, starting from the table of contents to locate relevant
   sections efficiently rather than OCR'ing the whole book blind.
3. **Extract the specific passage**, not the whole book at once. Pull
   only what's needed for the current gap (e.g. the tawakkul-related
   pages, not all 156 pages of a dua compilation in one pass).
4. **Write the structured entry** matching the existing schema in the
   target file exactly (same field names, same field order as sibling
   entries) — see `duas.json`/`quran_verses.json`/`prophets.json` for
   the pattern. Every new entry's `"primary_source"` names the actual
   file and, where practical, a page/chapter reference — never
   "Unknown source reference."
5. **Set the three verification fields honestly.** `citation_verified`
   and `source_verified` can be `true` if you actually named a real
   source and checked the entry's content against it during extraction
   (as done for dua_005/dua_006/qv_004/qv_005/prophet_yunus). Always set
   **`scholarly_reviewed: false`** on every new entry, without
   exception — extraction is not scholarly review, see
   `review_workflow.md`. This field only flips to `true` after an actual
   qualified external reviewer checks it.
6. **Update `sources/islamic_books/CATALOG.md`'s extraction-status table**
   for that book — what was pulled, what's still available for later.
7. **Register in `knowledge_index.json`** if a new file/category was
   created (not needed if adding entries to an existing file).
8. **Run `tools/validate_repo.py`** — confirms JSON validity, no
   duplicate IDs, and surfaces the new entries in the
   unreviewed-Islamic-content count on `REPO_HEALTH_REPORT.md`.
9. **Log the change in `CHANGELOG.md`** per `change_log_policy.md` —
   name the exact file(s) touched and what was verified.

## What this pipeline deliberately does NOT automate
Steps 1 (license judgment) and 5 (human review) are not automatable —
they require actual human judgment about permission and religious
accuracy. This pipeline speeds up steps 2-4 and 6-9 (the mechanical
parts); it does not remove the two steps that need a person.

## Related Files
`sources/islamic_books/CATALOG.md`,
`phase1/docs/governance/review_workflow.md`,
`phase1/docs/governance/change_log_policy.md`, `tools/validate_repo.py`
