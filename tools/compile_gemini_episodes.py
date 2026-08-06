#!/usr/bin/env python3
"""Real episode compiler v2 (v2.57) -- now uses scene_contract.json as
the AUTHORITATIVE source for visible characters and performance
ownership. That data is human-structured, not automated-guessed;
per-event certainty still varies and is recorded on each event's own
confidence field (CONFIRMED vs INFERRED_FROM_ORDER_AND_CONTENT) --
"human-structured" describes the process, not a claim that every
individual fact was independently verified. Still pulls
image_prompts.md/animation_directions.md for the creative visual/
choreography prose. This replaces v1's attempt to guess characters and
performers from unstructured scene_breakdown.md prose -- confirmed via
real diagnosis (v2.56 review) that prose parsing could not reliably
resolve either question. Separate from the frozen song compiler."""
import os, re, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gemini_shared import strip_dependencies, strip_scaffold, compute_content_hash, truncate_at_sentence, check_text_integrity

COMPILER_VERSION = "2.0"

def parse_episode_image_blocks(text):
    blocks = {}
    parts = re.split(r"## Block \d+ — Scene (\d+)[^\n]*\n", text)
    for i in range(1, len(parts), 2):
        if i < len(parts):
            content = parts[i+1] if i+1 < len(parts) else ""
            blocks[parts[i]] = content.split('"')[1] if '"' in content else content.strip()
    return blocks

def parse_animation_blocks(text):
    blocks = {}
    parts = re.split(r"## Block \d+ — Scene (\d+)\n", text)
    for i in range(1, len(parts), 2):
        if i < len(parts):
            blocks[parts[i]] = parts[i+1].strip() if i+1 < len(parts) else ""
    return blocks

ALL_ISSUES = []

def compile_episode(ep_dir, char_id_to_name, voice_identity_map):
    ep_id = os.path.basename(ep_dir)
    contract_path = os.path.join("production/episodes", ep_id, "scene_contract.json")
    if not os.path.exists(contract_path):
        ALL_ISSUES.append(f"{ep_id}: NO scene_contract.json found -- this episode has not been migrated to the structured schema. Not compiled from ambiguous prose (that approach was confirmed unreliable in the v2.56 diagnosis).")
        return 0
    contract = json.load(open(contract_path))

    def read(fname):
        p = os.path.join(ep_dir, fname)
        return open(p, encoding="utf-8").read() if os.path.exists(p) else ""

    image_blocks = parse_episode_image_blocks(read("image_prompts.md"))
    anim_blocks = parse_animation_blocks(read("animation_directions.md"))
    source_hash = compute_content_hash(read("scene_breakdown.md"), read("image_prompts.md"),
                                        read("dialogue.md"), read("animation_directions.md"),
                                        json.dumps(contract))

    gemini_dir = os.path.join(ep_dir, "Gemini")
    os.makedirs(gemini_dir, exist_ok=True)
    manifest_scenes = []

    for scene in contract["scenes"]:
        num = scene["scene_id"].split("_")[-1]
        visual = strip_scaffold(image_blocks.get(num, ""))
        anim = strip_scaffold(anim_blocks.get(num, ""))
        visual_text = truncate_at_sentence(visual, max_chars=2500) if visual else "(not found in image_prompts.md)"

        char_names = [char_id_to_name.get(cid, cid) for cid in scene["visible_characters"]]

        voice_lines = []
        for cid in scene["visible_characters"]:
            vid = voice_identity_map.get(cid)
            name = char_id_to_name.get(cid, cid)
            if vid:
                voice_lines.append(f"VOICE — {name}: {vid}")
        voice_section = "\n".join(voice_lines) if voice_lines else "(no registered voice identity for visible characters this scene)"

        perf_lines = []
        for e in scene["performance_events"]:
            name = char_id_to_name.get(e["character_id"], e["character_id"])
            perf_lines.append(f'{name} — {e["type"]}:\n"{e["text"]}"')
        perf_section = "\n\n".join(perf_lines) if perf_lines else "(no performance events recorded for this scene -- see visible_characters_confidence for why)"

        prompt = f"""# READY-TO-PASTE GEMINI PROMPT — {ep_id} Scene {num}

EPISODE ID: {ep_id}
SCENE ID: {scene['scene_id']}
DURATION: {scene['duration_seconds']}s
VISUAL/ANIMATION STYLE: Pixar/Illumination-quality 3D animation, soft rounded shapes, warm pastel color grading, clean child-safe character design, cinematic softbox lighting, modest clothing, wholesome mood.

LOCATION: {scene['location']}

VISIBLE CHARACTERS: {', '.join(char_names)}

VOICE IDENTITY:
{voice_section}

PERFORMANCE EVENTS:
{perf_section}

VISUAL: {visual_text}

ANIMATION: {anim if anim else '(not specified in source for this scene)'}

SAFETY/RELIGIOUS CONSTRAINTS: no fabricated religious quotation; family-friendly, modest, non-violent content only.

NEGATIVE CONSTRAINTS: do not alter character appearances from the locks above. Do not add characters not listed. Do not exceed {scene['duration_seconds']}s. Do not invent dialogue beyond the performance events listed above.
"""
        prompt = strip_dependencies(prompt)
        assert not re.search(r"\.md\b|\.json\b", prompt), f"{ep_id} scene {num}: EXTERNAL_DEPENDENCY leak"
        text_issues = check_text_integrity(prompt)
        assert not text_issues, f"{ep_id} scene {num}: TEXT_INTEGRITY issues: {text_issues}"
        assert not re.search(r"\b\w+'s\.\s|\b\w+'s\n\n", prompt), f"{ep_id} scene {num}: possible dangling possessive artifact"

        fname = f"scene_{num}.md"
        scene_hash = compute_content_hash(prompt)
        open(os.path.join(gemini_dir, fname), "w", encoding="utf-8").write(prompt)

        # Problem 2 fix: real ambiguity that affects a performance event
        # must be visible at the manifest level, not just an inert note
        has_perf_ambiguity = bool(scene.get("note", "").startswith("SOURCE_AMBIGUITY")) and bool(scene["performance_events"])
        # Problem 3 fix: reuse the existing --final gate pattern (songs,
        # v2.38) rather than invent a new mechanism -- a scene where
        # every performance event is INFERRED (none CONFIRMED) needs
        # the same real resolution step before final packaging
        confidences = [e["confidence"].split(" — ")[0] for e in scene["performance_events"]]
        all_inferred = bool(confidences) and all(c == "INFERRED_FROM_ORDER_AND_CONTENT" for c in confidences)
        # Problem 4 fix: real, computed flag -- not a guessed sub-beat count
        long_scene = scene["duration_seconds"] and scene["duration_seconds"] > 35

        manifest_scenes.append({
            "scene_id": scene["scene_id"], "duration": scene["duration_seconds"],
            "visible_characters": scene["visible_characters"],
            "speaking_characters": sorted(set(e["character_id"] for e in scene["performance_events"])),
            "gemini_prompt_file": fname, "scene_contract_hash": scene_hash,
            "performance_confidence_summary": confidences,
            "has_unresolved_performance_ambiguity": has_perf_ambiguity,
            "all_performance_events_inferred": all_inferred,
            "requires_resolution_before_final": has_perf_ambiguity or all_inferred,
            "long_scene_single_shot": long_scene,
        })
        if has_perf_ambiguity:
            ALL_ISSUES.append(f"{ep_id} {scene['scene_id']}: BLOCKED_PENDING_RESOLUTION -- {scene['note']}")

    manifest = {"episode_id": ep_id, "scene_count": len(contract["scenes"]), "actual_scene_files": len(manifest_scenes),
                "build_metadata": {"compiler_version": COMPILER_VERSION, "source_content_hash": source_hash,
                                    "schema": "scene_contract.json v1.0 (human-structured migration; per-event certainty varies -- see each event's own confidence field, not this schema label)"},
                "scenes": manifest_scenes}
    assert manifest["scene_count"] == manifest["actual_scene_files"], f"{ep_id}: MANIFEST_MISMATCH"
    json.dump(manifest, open(os.path.join(gemini_dir, "scene_manifest.json"), "w"), indent=2, ensure_ascii=False)
    return len(contract["scenes"])

if __name__ == "__main__":
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(repo_root)
    char_lib = json.load(open("sources/characters/character_master_library.json"))
    char_id_to_name = {c["character_id"]: c["canonical_name"].split("(")[0].strip() for c in char_lib["characters"]}
    voice_identity_map = {c["character_id"]: (c.get("voice_master") or {}).get("voice_identity_id") for c in char_lib["characters"]}

    targets = sys.argv[1:] if len(sys.argv) > 1 else ["ep_tawakkul_lost_toy", "ep_honesty_wallet_assisted"]
    for target in targets:
        ep_dir = os.path.join("output_package", target)
        if os.path.isdir(ep_dir):
            n = compile_episode(ep_dir, char_id_to_name, voice_identity_map)
            print(f"{target}: {n} scenes compiled")
    print(f"\nHonest diagnostics ({len(ALL_ISSUES)}):")
    for i in ALL_ISSUES:
        print(" -", i)
