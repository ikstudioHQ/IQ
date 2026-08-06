# Source-of-Truth Manifest

One authoritative home per kind of fact. Do not create a second one.

| Domain | Authoritative file |
|---|---|
| Character identity, visual appearance, wardrobe defaults | `sources/characters/character_master_library.json` |
| Voice identity (fingerprint, status, provider binding) | `character_master_library.json`'s `voice_master` field per character — NOT a separate file |
| Voice collision review | `sources/characters/voice_collision_matrix.json` (derived/review-only, not authoritative identity) |
| Pronunciation | `sources/production/pronunciation_dictionary.json` |
| Locations | `sources/production/location_library.json` |
| Wardrobe (non-default variants) | `sources/production/wardrobe_library.json` |
| Props | `sources/production/prop_registry.json` |
| Religious evidence (Quran/Hadith/Dua/Prophet) | `phase2/data/islamic/*.json` |
| Concept coverage | `phase3/knowledge/concepts/*.json` |
| Episode topic planning | `phase5/orchestration/planning/episode_topic_bank.json` |
| Song topic planning | `phase5/orchestration/planning/song_topic_bank.json` |
| Content restrictions | `phase2/data/safety/content_restrictions.json` |
| World/continuity history (concept usage, pattern usage) | `phase2/data/database/world_state.json` |
| Gemini export | Derived snapshot only — `output_package/<name>/gemini/*` — never authoritative, never hand-edited as a source of truth |

## Rule
If new information doesn't clearly belong to one of the rows above, extend
the closest existing file rather than creating a new one. A genuinely new
domain (e.g. a real episode/song production registry, a relationship graph)
should be added as a new row here at the same time it's created — this
table itself is the map future work checks before adding anything.

## Explicitly NOT built this pass (scoped out, not forgotten)
Full production/episode registry, relationship graph, canon-fact registry,
retcon/change-tracking system, pre-production resolver, failed-generation
memory, publishing state machine. These are real, sensible future
additions once real production (not speculative infrastructure) creates
an actual need for them — building them now, with no episodes/songs
actually published yet, risks exactly the "overbuilding" the source
material itself warned against.
