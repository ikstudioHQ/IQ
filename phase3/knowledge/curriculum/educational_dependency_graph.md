# Educational Dependency Graph — Learning Progression

## Version: 1.1

## Purpose
The AI must understand the exact order of learning concepts to maintain curriculum progression.

## Dependency Chain (Core Path)

```
Allah (Creator, Kind, One)
  ↓
Creation (World, Nature, Animals)
  ↓
Animals (Kindness, Care, Responsibility)
  ↓
Gratitude (Thanking Allah, Alhamdulillah)
  ↓
Parents (Respect, Kindness, Obedience with Love)
  ↓
Prayer (Connection, Remembering Allah)
  ↓
Community (Helping Others, Sharing)
  ↓
Leadership (Being a Good Example, Kind Leadership)
```

## Age-Based Dependency Mapping

### Age 2
Prerequisites: None (starting point)
Core Concepts: Allah, Kind, Gentle, Bismillah

### Age 3
Prerequisites: Age 2 concepts
Core Concepts: Prophets (Nuh — patience), Morning Dua, Sharing

### Age 4
Prerequisites: Age 3 concepts
Core Concepts: Ramadan (beautiful month), Parents (respect), Nature (gift)

### Age 5
Prerequisites: Age 4 concepts
Core Concepts: Good Manners (Akhlaq), Gratitude, Friendship

### Age 6
Prerequisites: Age 5 concepts
Core Concepts: Hajj (beautiful journey), Eid (joy), Prayer awareness

### Age 7
Prerequisites: Age 6 concepts
Core Concepts: Community, Deeper Islamic values, Basic prayer concepts

### Age 8
Prerequisites: Age 7 concepts
Core Concepts: Leadership, Kindness in action, Expanded vocabulary, Moral reasoning

## Trust in Allah (t_tawakkul) — added v2.5
Sits after the Prophets branch (`t_prophets_intro` → `t_prophet_nuh` /
`t_tawakkul`), consistent with `ADR_003_curriculum_order.md`'s reasoning:
tawakkul is an abstract concept requiring the concrete-empathy grounding of
the Prophets stories first (Nuh's patience, Yunus's trust in the whale).
Age range 5-7. Supported by real, page-cited sources — see
`phase2/data/islamic/duas.json` (dua_005, dua_006) and
`phase2/data/islamic/quran_verses.json` (qv_004, qv_005).

## Source References
- `phase3/knowledge/curriculum/knowledge_curriculum.json`
- `phase2/data/islamic/good_manners.json`
- `phase2/data/islamic/duas.json`
- `phase2/data/islamic/prophets.json`
- `phase2/data/islamic/quran_verses.json`

## Confidence
- System: `verified`
- Source: Curriculum design philosophy + educational psychology
- Reviewed: `true`
- Last Updated: `2026-07-31`
