# Authority Hierarchy — Repository Priority Order

## Priority (Highest to Lowest)
1. DESIGN_PRINCIPLES.md (Constitution — non-negotiable rules, philosophy, quality)
2. RULES.md / ISLAMIC.md / phase1/docs/governance/* (Universal content and Islamic rules, plus the operational governance layer that enforces them — authority_rules.md, conflict_resolution.md, review_workflow.md, deprecation_policy.md, versioning_policy.md, change_log_policy.md all sit at this tier, alongside RULES.md/ISLAMIC.md)
3. Knowledge JSON/YAML (verified data: characters, curriculum, world, language, islamic)
4. Template / Prompt Files (structured generation instructions, including MASTER_PROMPT.md itself)
5. Generated Output (produced by Master Prompt, must conform to 1-4)

When conflicts exist: higher priority wins. Lower priority never overrides higher.

This explicitly resolves a previously-undefined case: `phase1/docs/governance/review_workflow.md`'s `human_reviewed` gate is tier 2, and outranks any tier-4 prompt instruction (including in `MASTER_PROMPT.md`) that would treat `"scholarly_review_status": "verified"` alone as sufficient for publication. See `phase1/docs/governance/conflict_resolution.md`.
