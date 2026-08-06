# AI Bootstrap — Read This First

Generated artifact, derived from canonical sources. Do not hand-edit facts here — fix the source and regenerate.

## Identity
Repository version: **v2.40** | Architecture: **FROZEN** | Content Safety: **FROZEN** | Publication Gate: **FROZEN**
Live counts: see `generated/repository_fingerprint.json` (regenerate before trusting stale numbers).

## Authority hierarchy (unchanged, see `AUTHORITY_HIERARCHY.md`)
1. `DESIGN_PRINCIPLES.md` 2. `phase1/docs/governance/*` 3. Knowledge JSON/YAML 4. Templates/prompts 5. Generated output.

## Where everything is (see `generated/source_of_truth_registry.json` for the full machine-readable version)
Characters/voices → `sources/characters/character_master_library.json` | Locations/wardrobe/props → `sources/production/*.json` | Religious evidence → `phase2/data/islamic/*.json` | Concepts → `phase3/knowledge/concepts/*.json` | Safety → `phase2/data/safety/*.json` | Episode/song planning → `phase5/orchestration/planning/*.json` | Gemini export → `output_package/<name>/gemini/` (derived, never canonical) | Validator entry point → `tools/validate_repo.py` | Generation entry point → `MASTER_PROMPT.md` | Production entry point → `tools/package_episode.py`.

## Never scan unless the task specifically needs it
`research/`, `psychology/`, `tests/fixtures/` — old foundational reference material, not consumed by the live pipeline. `output_package/*` (except when checking/packaging a specific episode) — generated, not canonical. `phase4/engine/` — legacy, predates current architecture.

## Generated-only (regenerate, never hand-edit)
`generated/repository_fingerprint.json`, `generated/source_of_truth_registry.json`, `generated/feature_registry.json`, `generated/task_router.json`, `REPO_HEALTH_REPORT.md` (validator-written).

## Deprecated / historical (do not treat as current)
`FINAL_AUDIT_REPORT.md`, `VALIDATION_MATRIX.md`, `execution_policy.json` (all v1.1, dated before this project's active development — self-marked superseded, kept for history).

## Current known limitations
0 published episodes/songs (18 real test packages exist, none published). Voice provider/IDs null for all 82 speaking characters (audition-ready, not auditioned). 7/59 religious records still uncited. 0 scholarly review completed anywhere.

## Roadmap
Per the last governance audit (v2.40): **START_PRODUCTION** — next real step is one real pilot episode, not more infrastructure.

## Task routing
See `generated/task_router.json` for which files to load per task type instead of scanning the repository.
