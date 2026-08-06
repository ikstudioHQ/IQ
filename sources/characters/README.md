# Character Module — Islamic Kids Studio (@IslamicKidsHQ)

**Module Name:** Character Design System  
**Module Version:** v2.0  
**Repository Version:** v2.2  
**Status:** Production  
**Brand:** Islamic Kids Studio / @IslamicKidsHQ  
**Local Operation:** Confirmed (`local_only: true`)  
**Last Updated:** 2026-07-30  

---

## Purpose

This module converts the original Fixed Character Design Prompt System (v2) into a modular Character Knowledge Module for the Islamic Kids Studio Creator OS. All original prompts are preserved exactly — no simplification, shortening, or rewriting.

---

## Module Architecture

```
sources/characters/
├── README.md                          (this file)
├── character_system.md                (full original system: title, how-to-use, universal render suffix)
├── character_index.json               (retrieval index for all character files)
├── character_schema.json              (data schema for character references)
├── character_generation_rules.md      (master turnaround + hero portrait generation rules)
├── character_render_rules.md          (universal render suffix + visual/render specifications)
├── character_consistency_rules.md     (4 consistency rules — exact original)
└── characters/
    ├── zayd.md                        (Character 1 — exact locked block + prompts)
    ├── amira.md                       (Character 2 — exact locked block + prompts)
    ├── dada_yusuf.md                  (Character 3 — exact locked block + prompts)
    ├── baba_ahmad.md                  (Character 4 — exact locked block + prompts)
    ├── ummi_layla.md                  (Character 5 — exact locked block + prompts)
    └── nuri.md                        (Character 6 — exact locked block + prompts)
```

---

## Preservation Guarantee

Every character prompt (locked description blocks, master turnaround prompts, hero portrait prompts, universal render suffix, consistency rules, and system instructions) is preserved exactly from the original `Islamic_Kids_Studio_Character_Prompts.txt` attachment. No text has been altered, summarized, or rewritten.

---

## How This Module Works with MASTER_PROMPT.md

The `MASTER_PROMPT.md` (Creator OS Master Prompt) orchestrates this module automatically:

1. **Load Character System** — reads `character_system.md` (cached if already loaded).
2. **Load Character Index** — reads `character_index.json` to confirm file paths.
3. **Load Only Required Character Files** — selects active characters from `characters/*.md` based on episode requirements. Never loads unrelated character files.
4. **Use Locked Description Blocks Exactly** — copies the locked description block from the selected character file word-for-word into any scene prompt. Never paraphrases or shortens the block.
5. **Never Modify Locked Character Descriptions** — the locked description block is immutable. It may only be referenced, never edited or interpreted differently.
6. **Generate Turnaround Prompts Only When Creating New Character References** — master turnaround prompts (`MASTER TURNAROUND PROMPT`) are generated only when a new character reference is needed. Existing references (`characters/*.md`) are reused directly.
7. **Reuse Existing Character References in Future Episodes** — for every future scene/video, the system loads the exact locked description block from the existing `.md` file. It does not regenerate or reinterpret the character design.

---

## Key Design Principles (From `DESIGN_PRINCIPLES.md`)

- **No Copyrighted Characters:** All 6 characters (Zayd, Amira, Dada Yusuf, Baba Ahmad, Ummi Layla, Nuri) are original.
- **Fixed Design Lock:** Once a master turnaround prompt is generated and saved as reference, the locked description block becomes the single source of truth.
- **Consistency Across All Episodes:** Every scene using a character must use the identical locked description text to ensure visual consistency (same DSLR-style reference system as Bible Story Network).
- **Modular Retrieval:** Only required character files are loaded per episode. The full repository is never scanned unnecessarily.
- **Local-Only:** No remote dependencies. All files are relative paths from workspace root.

---

## File Reference Map

| File | Content | Usage |
|---|---|---|
| `character_system.md` | Full original v2 system intro + how-to-use + universal render suffix | Reference for system behavior |
| `character_index.json` | Index mapping concepts (`zayd`, `amira`, `dada_yusuf`, `baba_ahmad`, `ummi_layla`, `nuri`) to file paths | Retrieval by `MASTER_PROMPT.md` |
| `character_schema.json` | Schema for character entries (name, role, version, locked_description, master_turnaround, hero_portrait) | Validation of character data |
| `character_generation_rules.md` | Rules for generating master turnaround and hero portrait prompts | When creating new references |
| `character_render_rules.md` | Universal render suffix text + visual/render specifications | Every image prompt must close with this suffix |
| `character_consistency_rules.md` | 4 exact consistency rules from original file | Mandatory for all future scene prompts |
| `sources/characters/characters/zayd.md` | Character 1: locked description, master turnaround, hero portrait | Episode scene prompts |
| `sources/characters/characters/amira.md` | Character 2: locked description, master turnaround, hero portrait | Episode scene prompts |
| `sources/characters/characters/dada_yusuf.md` | Character 3: locked description, master turnaround, hero portrait | Episode scene prompts |
| `sources/characters/characters/baba_ahmad.md` | Character 4: locked description, master turnaround, hero portrait | Episode scene prompts |
| `sources/characters/characters/ummi_layla.md` | Character 5: locked description, master turnaround, hero portrait | Episode scene prompts |
| `sources/characters/characters/nuri.md` | Character 6: locked description, master turnaround, hero portrait | Episode scene prompts |

---

## Character Versions

Each character file preserves the original design lock. There is no version override within the individual prompts — the module relies on the file-level preservation and the `MASTER_PROMPT.md` reference to `character_versions.json` for any future updates. Updates must follow the module's update rules (new file version, new master turnaround, new locked block — never silent modification of existing `.md` content).

---

## Integration with Repository Modules

- **Design Principles (`DESIGN_PRINCIPLES.md`):** Character designs must remain merchandise-friendly, soft-rounded, warm-pastel, and child-safe.
- **Brand (`BRAND.md`):** All character visuals must use `Islamic Kids Studio` palette and style.
- **Rules (`RULES.md`):** No copyrighted characters; no invented sources; consistent personalities.
- **Knowledge Index (`knowledge_index.json`):** Registered under `characters` concept key (updated).
- **Repository Manifest (`repository_manifest.json`):** Character Module added to supported modules.
- **MASTER_PROMPT.md:** Orchestrates this module automatically via Character Module workflow steps.

---

## Future Expansion (Module-Level)

- New characters: Add new `.md` file in `characters/` + update `character_index.json` + update `character_schema.json`.
- New languages: Expand locked descriptions with translated text (separate file, never overwrite original).
- New render engines: Update `character_render_rules.md` with new suffix options while preserving original.
- Interactive content: Reference `characters/*.md` in interactive prompts without altering locked blocks.

---

## Related Repository Files

- `DESIGN_PRINCIPLES.md` (Constitution — non-negotiable design rules)
- `MASTER_PROMPT.md` (Creator OS Master Prompt — orchestrates this module)
- `knowledge_index.json` (retrieval index — includes this module)
- `repository_manifest.json` (repository manifest — includes Character Module)
- `phase3/knowledge/characters/knowledge_characters.json` (existing knowledge base — complements this module)
- `phase2/data/database/character_versions.json` (version tracking — references this module)
- `phase2/data/database/character_relationships.json` (relationship tracking — references character names from this module)

---

## Audit & Validation

- Zero broken references: All links in this file point to existing repository files.
- Zero contradictions: Module rules align with `DESIGN_PRINCIPLES.md`, `RULES.md`, and `MASTER_PROMPT.md`.
- Zero placeholders: All file paths, versions, and references are concrete.
- Zero rewrites: Every original prompt preserved exactly.
- Zero structural redesign: Module fits into existing repository architecture without restructuring other phases.

---

*This module is complete, production-ready, and fully integrated into the Islamic Kids Studio Creator OS.*
