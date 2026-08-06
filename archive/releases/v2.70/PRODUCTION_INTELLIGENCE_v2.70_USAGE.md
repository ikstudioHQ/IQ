# Production Intelligence v2.70

Accepted memory is committed only after explicit acceptance. Draft generation never becomes canonical memory. Story arcs are derived from the active roadmap and validated for episode/setup/payoff ordering. Character development is stored separately from immutable character identity. Song planning returns NO_SONG, USE_CANONICAL_SONG, or SONG_REVIEW_REQUIRED. Clip repair is failure-specific and changes only the affected unit data.

Commands:
- `python3 tools/episode_autopilot.py generate-one <immutable_episode_id>`
- `python3 tools/episode_autopilot.py generate-range <order-or-id> <order-or-id>`
- `python3 tools/episode_autopilot.py accept <immutable_episode_id>`
- `python3 tools/episode_autopilot.py validate <immutable_episode_id>`

Human render QA and Islamic publication approval remain separate gates.
