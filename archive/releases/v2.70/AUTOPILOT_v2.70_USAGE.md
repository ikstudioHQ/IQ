# Autopilot v2.69

The v2.68 deterministic episode pipeline now reads `production/roadmaps/active_roadmap.json` and therefore works with arbitrary roadmap lengths and immutable roadmap episode IDs.

Generate one: `python3 tools/episode_autopilot.py generate-one <episode_id>`

Generate range remains available for legacy numeric roadmaps; dynamic-roadmap production should use immutable episode IDs through generate-one until range selection is upgraded to order-based IDs.

Validate: `python3 tools/episode_autopilot.py validate <episode_id>`

Draft production never promotes Islamic verification/review states. FINAL publication remains fail-closed.

## v2.70
Dynamic `generate-range` accepts active roadmap order numbers or immutable roadmap episode IDs. `accept` commits an accepted memory snapshot; draft generation does not.
