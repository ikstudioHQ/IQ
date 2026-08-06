# Developer Startup Guide (15-minute version)

**Read `AI_BOOTSTRAP.md` first** — this file expands on it, doesn't replace it.

## Architecture
FROZEN since v2.30 (Content Safety since v2.36, Publication Gate since v2.38).
Do not modify without a *reproducible* production bug — "could be nicer" is not sufficient.

## Execution flow
Topic → real evidence retrieval (`phase2/data/islamic/`) → script (per `MASTER_PROMPT.md`) →
`episode_consistency_check.py` (character/religious/safety validation) →
`package_episode.py` (DRAFT by default, `--final` requires safety resolution) → zip.

## Authority hierarchy
See `AUTHORITY_HIERARCHY.md`. Constitution > governance > knowledge data > templates > generated output.

## Canonical vs generated
Canonical = `sources/`, `phase2/data/`, `phase3/knowledge/`, `phase5/orchestration/planning/`.
Generated = `output_package/`, `generated/`, `REPO_HEALTH_REPORT.md`. Never treat generated as a fact source.

## Adding things safely
Character: `sources/characters/ADD_NEW_CHARACTER.md`. Religious evidence: real web search → verify → cite, never model memory. Location/wardrobe/prop: extend the existing `sources/production/*.json` array, don't create a new file. Safety rule: append to `content_scene_safety_registry.json`, don't build a second checker.

## Validating
`python3 tools/validate_repo.py .` — whole repo. `python3 tools/episode_consistency_check.py check-episode <dir> .` — one package.

## Publishing
`python3 tools/package_episode.py <slug>` — draft. Add `--final` only once safety review_required items (if any) have a real resolution in `phase2/data/safety/review_resolutions.json`.

## Known limitations right now
0 published episodes/songs. No real voice provider selected for any of the 82 speaking characters. 7/59 religious records still uncited. 0 scholarly review completed.

## Do not duplicate
Check `generated/source_of_truth_registry.json` before creating any new file that might already have a home.
