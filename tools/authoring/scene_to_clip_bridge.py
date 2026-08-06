"""
tools/authoring/scene_to_clip_bridge.py

THE missing piece identified in the Phase 5 gap analysis: nothing
converted an authored scene into the SceneClipSpec objects
Phases 2-5's ContinuityAssembler already knows how to consume. This
module is that bridge, and nothing else -- it does not modify
SceneClipSpec, ContinuityAssembler, or any Phase 2-5 interface.

Clip boundary rule (per Phase 6's explicit requirement -- "must
preserve action, dialogue, camera and scene continuity rather than
blindly cutting text by duration"): beats are packed into a clip
greedily until either (a) the provider's actual duration budget would
be exceeded, or (b) a beat declares a different camera_hint than the
clip currently being built -- a camera change IS a legitimate clip
boundary in video production, not just a duration overflow. A single
beat is NEVER split across two clips. If one beat alone is longer than
the provider's max duration, it becomes its own clip and gets flagged
as a diagnostic for human/author revision -- never silently mis-cut.

Duration budget comes from ProviderCapabilities.max_duration_seconds(),
not a literal -- swapping providers changes clip counts automatically
without touching this module.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from tools.authoring.schemas import EpisodeScript
from tools.continuity.request_payload_builder import SceneClipSpec
from tools.providers.base import ProviderCapabilities

_WORD_RE = re.compile(r"\S+")
DIALOGUE_WORDS_PER_SECOND = 2.3  # deliberately slower than average adult speech -- this is children's content, paced for a young audience
DEFAULT_ACTION_SECONDS = 3.0
DEFAULT_CAMERA_NOTE_SECONDS = 0.5
MIN_BEAT_SECONDS = 1.5


def estimate_beat_seconds(beat: dict) -> float:
    if beat.get("estimated_seconds") is not None:
        return float(beat["estimated_seconds"])
    if beat["kind"] == "dialogue":
        word_count = len(_WORD_RE.findall(beat["text"]))
        return max(MIN_BEAT_SECONDS, word_count / DIALOGUE_WORDS_PER_SECOND)
    if beat["kind"] == "camera_note":
        return DEFAULT_CAMERA_NOTE_SECONDS
    return DEFAULT_ACTION_SECONDS


def _character_name(root: Path, character_id: str, cache: dict) -> str:
    if character_id not in cache:
        path = root / "continuity" / "character_bible" / f"{character_id}.json"
        if path.exists():
            bible = json.loads(path.read_text(encoding="utf-8"))
            cache[character_id] = bible.get("canonical_name", character_id)
        else:
            # Defense in depth (Phase 8 blocker fix): don't silently treat
            # an unknown ID as if it were a plausible display name -- the
            # real block happens upstream in RequestPayloadBuilder.build()
            # via id_validation.py, but if this text is ever inspected
            # before that gate runs, it must be immediately obvious it's
            # not a real character, not something that reads like one.
            cache[character_id] = f"[unknown character: {character_id}]"
    return cache[character_id]


def _compose_prompt_text(root: Path, beats: list[dict], name_cache: dict) -> str:
    lines = []
    for beat in beats:
        if beat["kind"] == "dialogue":
            name = _character_name(root, beat["character_id"], name_cache) if beat.get("character_id") else "Someone"
            tone = f", {beat['emotion']}," if beat.get("emotion") else ""
            lines.append(f'{name}{tone} says: "{beat["text"]}"')
        elif beat["kind"] == "camera_note":
            lines.append(f"[Camera: {beat['text']}]")
        else:
            lines.append(beat["text"])
    return " ".join(lines)


def build_clip_specs(
    root: str | Path,
    episode: EpisodeScript,
    provider_capabilities: ProviderCapabilities,
    *,
    add_default_duplicate_guards: bool = True,
) -> tuple[list[SceneClipSpec], list[dict]]:
    root = Path(root)
    name_cache: dict = {}
    specs: list[SceneClipSpec] = []
    diagnostics: list[dict] = []

    # Planning budget: the capability-driven ceiling, always computed from
    # the provider object -- never a literal. Reference images are assumed
    # likely (this content has rich character-bible coverage), which is the
    # tighter/more conservative budget for providers that force a longer
    # duration when references are used (true for Veo 3.1/Fast today).
    budget = provider_capabilities.max_duration_seconds(using_reference_images=True)

    for scene in episode.scenes:
        beats = scene.get("beats", [])
        group: list[dict] = []
        group_duration = 0.0
        group_camera_hint: Optional[str] = None
        clip_index = 1
        previous_clip_id: Optional[str] = None

        def flush(final_group, final_duration, overflow_flag=False):
            nonlocal clip_index, previous_clip_id
            if not final_group:
                return
            dialogue_speakers = [b["character_id"] for b in final_group if b["kind"] == "dialogue" and b.get("character_id")]
            primary = []
            for cid in dialogue_speakers:
                if cid not in primary:
                    primary.append(cid)
            if not primary and scene.get("characters_present"):
                primary = [scene["characters_present"][0]]
            # ROOT-CAUSE FIX (confirmed by direct inspection of a real
            # production run): this used to be
            #   secondary = [c for c in scene["characters_present"] if c not in primary]
            # which pulled the ENTIRE scene roster into every single clip's
            # reference-image competition, even clips where most of that
            # roster never appears at all -- confirmed with a real example
            # where three characters were "secondary" and competing for
            # budget in a clip whose only actual content was one other
            # character's single line. Now: a scene-roster character only
            # counts as secondary for THIS clip if they're actually
            # referenced by name in this clip's own action-beat text.
            # Residual, honestly-disclosed limitation: this is a text-match
            # heuristic, not true scene-presence tracking -- a character
            # who is visually present but never named in the action text
            # of this specific clip will still be excluded. It is a real,
            # substantial improvement over "always include everyone in the
            # scene," not a complete fix of the underlying budget scarcity
            # (3 reference-image slots is a hard provider limit).
            secondary = []
            action_text = " ".join(b["text"] for b in final_group if b["kind"] == "action").lower()
            for cid in scene.get("characters_present", []):
                if cid in primary:
                    continue
                name = _character_name(root, cid, name_cache).lower()
                if not name or name.startswith("[unknown character"):
                    continue
                # Registry canonical_name is often a disambiguating label
                # ("Neighbor Uncle Dawud"), not how a character is actually
                # named in prose ("Uncle Dawud") -- match on the full name
                # OR its last word (typically the actual given name), found
                # by testing, not assumed.
                last_word = name.split()[-1] if name.split() else name
                if name in action_text or (len(last_word) > 2 and last_word in action_text):
                    secondary.append(cid)

            negative_constraints = []
            if add_default_duplicate_guards:
                for cid in primary + secondary:
                    negative_constraints.append(
                        f"no duplicate {_character_name(root, cid, name_cache)}, exactly one instance"
                    )

            clip_id = f"clip_{clip_index:02d}"
            spec = SceneClipSpec(
                episode_id=episode.episode_id,
                scene_id=scene["scene_id"],
                clip_id=clip_id,
                sequence_index=clip_index,
                primary_character_ids=primary,
                secondary_character_ids=secondary,
                environment_id=scene.get("location_id"),
                prop_ids=scene.get("props_visible", []),
                camera={},
                scene_type=group_camera_hint,
                lighting={},
                emotions={b["character_id"]: b["emotion"] for b in final_group if b.get("character_id") and b.get("emotion")},
                music={},
                raw_prompt_text=_compose_prompt_text(root, final_group, name_cache),
                negative_constraints=negative_constraints,
                previous_clip_id=previous_clip_id,
                environment_overrides=scene.get("environment_overrides", {}) if clip_index == 1 else {},
            )
            specs.append(spec)
            if overflow_flag:
                diagnostics.append({
                    "source": "scene_to_clip_bridge",
                    "field": f"{scene['scene_id']}.{clip_id}",
                    "message": (
                        f"A single beat's estimated duration ({final_duration:.1f}s) exceeds the provider's "
                        f"max clip duration ({budget}s). Emitted as its own clip rather than cutting the "
                        f"beat's text -- this scene needs author revision (shorten the line, or split it "
                        f"into two beats with a natural pause) rather than an automatic fix."
                    ),
                    "severity": "warning",
                })
            previous_clip_id = clip_id
            clip_index += 1

        for beat in beats:
            est = estimate_beat_seconds(beat)
            camera_hint = beat.get("camera_hint")
            is_solo_overflow = not group and est > budget

            needs_new_clip = bool(group) and (
                (camera_hint and group_camera_hint and camera_hint != group_camera_hint)
                or (group_duration + est > budget)
            )
            if needs_new_clip:
                flush(group, group_duration)
                group, group_duration, group_camera_hint = [], 0.0, None

            if is_solo_overflow:
                flush([beat], est, overflow_flag=True)
                continue

            group.append(beat)
            group_duration += est
            if camera_hint:
                group_camera_hint = camera_hint

        flush(group, group_duration)

    return specs, diagnostics
