# Dynamic Roadmap v2.69

Create: `python3 tools/dynamic_roadmap.py create 30 --id roadmap_main --out production/roadmaps/active_roadmap.json`

Validate: `python3 tools/dynamic_roadmap.py validate production/roadmaps/active_roadmap.json`

Preview: `python3 tools/dynamic_roadmap.py preview production/roadmaps/active_roadmap.json`

The Python API exposes `create`, `validate`, `revise` (extend/shorten/lock), and `impact`. Episode IDs are immutable hashes independent of mutable display order. Historical v2.67 90-day content is archived and is not the active roadmap.
