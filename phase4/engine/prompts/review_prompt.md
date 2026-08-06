# Review Prompt — Prompt Module

> Version: 1.1 | Owner: Islamic Kids Studio AI System | Last Updated: 2026-07-30

---

# REVIEW PROMPT — Human & AI Review Process

## Purpose
Defines the review workflow for all generated content.

## Inputs
- Generated episode package
- QA report
- Brand requirements
- Islamic requirements

## Review Steps
1. AI Quality Check: Load `qa_prompt.md`, run full checklist.
2. Brand Consistency Check: Confirm `BRAND.md` compliance.
3. Islamic Accuracy Check: Confirm references and accuracy.
4. Parent Review (for new series): Confirm parent-approval.
5. Final Approval: Confirm all checks pass.

## Rules
- Never skip review steps.
- Always document errors in `generation_log.json`.
- Never publish content that fails Islamic accuracy.
- Always confirm brand consistency before packaging.

## Related Files
`MASTER.md`, `MEMORY.md`, `WORKFLOW.md`
