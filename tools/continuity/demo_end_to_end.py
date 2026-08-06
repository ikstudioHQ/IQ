#!/usr/bin/env python3
"""
tools/continuity/demo_end_to_end.py

Runs one real clip through the full Phase 2 pipeline and prints every
stage's actual output: Character Bible loaded, Environment Bible
loaded, Prop Registry loaded, Reference Image Manager's selection
decision, the provider-agnostic request, and the final provider-
specific payload. This is a demonstration/inspection script, not a
test -- it exists to make the "is the new foundation actually being
used" question answerable by reading real output, not by trusting a
claim.

Usage:
    python3 tools/continuity/demo_end_to_end.py [repo_root]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DEFAULT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DEFAULT))

from tools.continuity.assembler import ContinuityAssembler
from tools.continuity.request_payload_builder import SceneClipSpec
from tools.providers.veo31_fast import Veo31FastProvider


def _section(title: str) -> str:
    return f"\n{'=' * 70}\n{title}\n{'=' * 70}"


def run(root: Path) -> str:
    out = []

    spec = SceneClipSpec(
        episode_id="demo_ep_001",
        scene_id="scene_02",
        clip_id="clip_05",
        sequence_index=5,
        primary_character_ids=["char_002_amira"],
        secondary_character_ids=["char_001_zayd"],
        environment_id="loc_family_living_room",
        prop_ids=["prop_grocery_bag_01"],
        camera={},
        scene_type="curiosity_hook_opening",
        lighting={"time_of_day": "afternoon"},
        emotions={"char_002_amira": "curious", "char_001_zayd": "curious"},
        music={"cue_id": None, "notes": "ambient only"},
        raw_prompt_text=(
            "Amira and Zayd notice something unusual near the family Quran "
            "stand in the living room. They lean in to look closer."
        ),
        negative_constraints=["no duplicate characters", "no additional unlisted characters"],
        previous_clip_id=None,
    )

    out.append(_section("STAGE 0 -- Input: SceneClipSpec (from authoring layer, unchanged this phase)"))
    out.append(json.dumps({
        "episode_id": spec.episode_id, "scene_id": spec.scene_id, "clip_id": spec.clip_id,
        "primary_character_ids": spec.primary_character_ids,
        "secondary_character_ids": spec.secondary_character_ids,
        "environment_id": spec.environment_id, "prop_ids": spec.prop_ids,
        "scene_type": spec.scene_type, "raw_prompt_text": spec.raw_prompt_text,
    }, indent=2))

    from tools.continuity.reference_image_manager import ReferenceImageManager
    ref_mgr = ReferenceImageManager(str(root))

    out.append(_section("STAGE 1 -- Character Bible loaded (real files on disk)"))
    for cid in spec.primary_character_ids + spec.secondary_character_ids:
        bible_path = root / "continuity" / "character_bible" / f"{cid}.json"
        bible = json.loads(bible_path.read_text(encoding="utf-8"))
        out.append(f"  {cid}: canonical_name={bible['canonical_name']!r}, "
                    f"reference_images={len(bible['reference_images'])}, "
                    f"source={bible_path.relative_to(root)}")

    out.append(_section("STAGE 2 -- Environment Bible loaded"))
    env_path = root / "continuity" / "environment_bible" / f"{spec.environment_id}.json"
    env_bible = json.loads(env_path.read_text(encoding="utf-8"))
    out.append(f"  {spec.environment_id}: display_name={env_bible['display_name']!r}, "
                f"reference_images={len(env_bible['reference_images'])} "
                f"(0 expected -- see MIGRATION_REPORT.md), source={env_path.relative_to(root)}")

    out.append(_section("STAGE 3 -- Prop Registry loaded"))
    for pid in spec.prop_ids:
        prop_path = root / "continuity" / "prop_registry" / f"{pid}.json"
        prop_bible = json.loads(prop_path.read_text(encoding="utf-8"))
        out.append(f"  {pid}: display_name={prop_bible['display_name']!r}, "
                    f"reference_images={len(prop_bible['reference_images'])} "
                    f"(0 expected -- see MIGRATION_REPORT.md), source={prop_path.relative_to(root)}")

    out.append(_section("STAGE 4 -- Reference Image Manager: selection decision"))
    provider = Veo31FastProvider()
    caps = provider.capabilities()
    selected, dropped = ref_mgr.select_for_clip(
        primary_character_ids=spec.primary_character_ids,
        secondary_character_ids=spec.secondary_character_ids,
        environment_id=spec.environment_id,
        prop_ids=spec.prop_ids,
        capabilities=caps,
    )
    out.append(f"  Provider capability consulted: {caps.provider_id}, max_reference_images={caps.max_reference_images}")
    out.append(f"  SELECTED ({len(selected)}):")
    for a in selected:
        out.append(f"    - {a.owner_id} [{a.role}] -> {a.path}")
    out.append(f"  DROPPED/UNAVAILABLE ({len(dropped)}):")
    for d in dropped:
        out.append(f"    - {d}")

    out.append(_section("STAGE 5 -- Provider Adapter: capability enforcement"))
    out.append(f"  Provider: {caps.provider_id} ({caps.model_id})")
    out.append(f"  Duration forced to: "
                f"{caps.max_duration_seconds(using_reference_images=bool(selected))}s "
                f"(reference images in use -> forces 8s per capability rule)")

    out.append(_section("STAGE 6 -- Final provider-agnostic ContinuityRequest"))
    assembler = ContinuityAssembler(str(root), provider)
    request, payload, errors = assembler.process_clip(spec)
    out.append(json.dumps(request.to_dict(), indent=2))
    if errors:
        out.append(f"\n  Validation notes: {[e.message for e in errors]}")

    out.append(_section("STAGE 7 -- Final provider-specific payload (Veo 3.1 Fast shape)"))
    out.append(json.dumps(payload, indent=2))

    out.append(_section("STAGE 8 -- ClipState written back"))
    saved = assembler.clip_state_repo.load(spec.episode_id, spec.scene_id, spec.clip_id)
    out.append(f"  Saved to: continuity/clip_state/{spec.episode_id}/{spec.scene_id}/{spec.clip_id}.json")
    out.append(f"  qa_status={saved.qa_status}")

    return "\n".join(out)


def main(argv=None):
    root = Path(argv[0]).resolve() if argv else ROOT_DEFAULT
    print(run(root))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
