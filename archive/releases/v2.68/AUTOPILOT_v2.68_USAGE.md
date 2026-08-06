# v2.68 New Episode Autopilot

The Autopilot converts an existing canonical roadmap entry into a deterministic **draft** production package. Creative story text is `AUTHORED_CREATIVE_STORY`; staging is `AUTHORED_PRODUCTION_DIRECTION`. Neither is religious evidence or publication approval.

## One episode

`python3 tools/episode_autopilot.py generate-one ep_001`

Optional target story duration:

`python3 tools/episode_autopilot.py generate-one ep_001 --target-duration 600`

## Range

`python3 tools/episode_autopilot.py generate-range 1 4`

Episodes are processed sequentially.

## Validate

`python3 tools/episode_autopilot.py validate ep_001`

## Stage-aware regeneration

`python3 tools/episode_autopilot.py regenerate ep_001 --stage prompts`

The current deterministic implementation regenerates downstream draft artifacts from roadmap authority; it never promotes Islamic review states.

## Output

`production/autopilot/episodes/<episode_id>/` contains story script JSON, per-scene authored production plans, <=10-second Gemini prompts, QA report, and production manifest.

FINAL publication remains fail-closed under the existing Islamic review architecture. Prompt QA does not equal rendered-video approval.
