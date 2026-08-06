#!/usr/bin/env python3
"""Runtime compiler. Reads canonical sources, writes runtime/*.json.
Never edit runtime/ by hand -- rerun this script. Checksummed so
recompilation can be skipped when nothing canonical changed."""
import json, os, glob, hashlib, datetime

def get_repo_version():
    manifest = load("repository_manifest.json")
    version = (manifest or {}).get("repository_version")
    if not version:
        raise RuntimeError("repository_manifest.json has no repository_version")
    vc = open("VERSION_COMPATIBILITY.md", encoding="utf-8").read()
    import re
    m = re.search(r"Current Repository Version:\s*\*\*v([^*]+)\*\*", vc)
    if not m or m.group(1) != version:
        raise RuntimeError(f"repository version authorities disagree: manifest={version!r}, compatibility={m.group(1) if m else None!r}")
    return version


def load(path, default=None):
    try:
        return json.load(open(path))
    except Exception:
        return default

def checksum(*paths):
    h = hashlib.sha256()
    for p in sorted(paths):
        if os.path.exists(p):
            h.update(open(p, "rb").read())
    return h.hexdigest()[:16]

def stamp(sources, schema="1.0"):
    return {"generated_from": sources, "generated_at": "2026-08-05T00:00:00",
            "repository_version": get_repo_version(), "schema_version": schema,
            "checksum": checksum(*sources), "generator": "tools/compile_runtime.py v1.0"}

def compile_all():
    files_before = sum(1 for _ in glob.glob("**/*.json", recursive=True) if "runtime/" not in _)

    # runtime_characters: merge character + voice + collision, canonical IDs only
    src = ["sources/characters/character_master_library.json"]
    chars = load(src[0])
    compact = [{"id": c["character_id"], "name": c["canonical_name"], "role": c["role_relation"],
                "speaking": c["is_speaking"], "voice_id": (c.get("voice_master") or {}).get("voice_identity_id"),
                "tier": c.get("production_priority")} for c in chars["characters"]]
    out = {**stamp(src), "characters": compact}
    json.dump(out, open("runtime/runtime_characters.json", "w"), indent=2, ensure_ascii=False)

    # runtime_curriculum: concepts + evidence counts, canonical IDs only
    src = sorted(glob.glob("phase3/knowledge/concepts/*.json"))
    concepts = []
    for f in src:
        c = load(f)
        concepts.append({"id": c["concept_id"], "quran": c.get("related_quran", []), "hadith": c.get("related_hadith", []),
                          "duas": c.get("related_duas", []), "primary_pattern": (c.get("recommended_default") or {}).get("pattern_id")})
    out = {**stamp(src), "concepts": concepts}
    json.dump(out, open("runtime/runtime_curriculum.json", "w"), indent=2, ensure_ascii=False)

    # runtime_topics: episode + song planning, IDs + evidence only
    src = ["phase5/orchestration/planning/episode_topic_bank.json", "phase5/orchestration/planning/song_topic_bank.json"]
    ep = load(src[0], {"topics": []})["topics"]
    sg = load(src[1], {"song_topics": []})["song_topics"]
    out = {**stamp(src), "episode_topics": [{"id": t["topic_id"], "concept": t["primary_concept"], "readiness": t["production_readiness"]} for t in ep],
           "song_topics": [{"id": t["song_topic_id"], "concept": t["primary_concept"], "readiness": t["production_readiness"]} for t in sg]}
    json.dump(out, open("runtime/runtime_topics.json", "w"), indent=2, ensure_ascii=False)

    # runtime_world: locations + wardrobe + props, merged (small enough to not need separate files)
    src = ["sources/production/location_library.json", "sources/production/wardrobe_library.json", "sources/production/prop_registry.json"]
    loc = load(src[0], {"locations": []})["locations"]
    ward = load(src[1], {"wardrobes": []})["wardrobes"]
    prop = load(src[2], {"props": []})["props"]
    out = {**stamp(src), "locations": [{"id": l["location_id"], "name": l["name"]} for l in loc],
           "wardrobes": [{"id": w["wardrobe_id"], "character": w["character_id"]} for w in ward],
           "props": [{"id": p["prop_id"], "owner": p["owner"]} for p in prop]}
    json.dump(out, open("runtime/runtime_world.json", "w"), indent=2, ensure_ascii=False)

    # runtime_safety: rules index only, not full text
    src = ["phase2/data/safety/content_scene_safety_registry.json"]
    rules = load(src[0], {"rules": []})["rules"]
    out = {**stamp(src), "rules": [{"id": r["rule_id"], "category": r["category"], "decision": r["decision"]} for r in rules]}
    json.dump(out, open("runtime/runtime_safety.json", "w"), indent=2, ensure_ascii=False)

    # runtime_relationships: pass through the existing real graph (already compact)
    src = ["generated/relationship_graph.json"]
    rel = load(src[0], {"edges": []})
    out = {**stamp(src), "edges": rel.get("edges", []), "known_limitation": rel.get("note", "")[:200]}
    json.dump(out, open("runtime/runtime_relationships.json", "w"), indent=2, ensure_ascii=False)

    # runtime_index: task router + feature registry + fingerprint, merged into one lookup file
    src = ["generated/task_router.json", "generated/feature_registry.json", "generated/repository_fingerprint.json", "generated/source_of_truth_registry.json"]
    out = {**stamp(src, schema="1.0"),
           "task_router": load(src[0]), "features": load(src[1]),
           "fingerprint": load(src[2]), "source_of_truth": load(src[3])}
    json.dump(out, open("runtime/runtime_index.json", "w"), indent=2, ensure_ascii=False)

    # runtime_manifest: the entry point, describes the runtime package itself
    all_runtime = sorted(glob.glob("runtime/runtime_*.json"))
    manifest = {
        "repository_version": get_repo_version(), "generated_at": "2026-08-05T00:00:00",
        "runtime_files": [os.path.basename(f) for f in all_runtime if "manifest" not in f],
        "rule": "runtime/ is NEVER hand-edited. Rerun tools/compile_runtime.py after any canonical change. Each file's own 'checksum' field lets a caller detect staleness without re-reading canonical sources.",
        "files_scanned_for_compilation": files_before,
    }
    json.dump(manifest, open("runtime/runtime_manifest.json", "w"), indent=2, ensure_ascii=False)

    return files_before, len(all_runtime) + 1

if __name__ == "__main__":
    before, runtime_count = compile_all()
    print(f"Compiled {runtime_count} runtime files from {before} canonical JSON files scanned.")
