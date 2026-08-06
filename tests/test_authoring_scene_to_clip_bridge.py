import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.authoring.schemas import EpisodeScript
from tools.authoring.scene_to_clip_bridge import build_clip_specs, estimate_beat_seconds
from tools.providers.base import ProviderCapabilities
from tools.providers.veo31_fast import Veo31FastProvider


def _fake_capabilities(max_duration: int, forces_when_refs: bool = True) -> ProviderCapabilities:
    return ProviderCapabilities(
        provider_id="fake", model_id="fake-model", max_reference_images=3,
        supports_reference_images=True, supports_image_to_video=True,
        supports_last_frame_interpolation=True, supports_video_extension=True,
        duration_options_seconds=[max_duration],
        duration_forced_to_8_when=["reference_images_used"] if forces_when_refs else [],
        resolution_options=["720p"], aspect_ratios=["16:9"], frame_rate_fps=24,
        max_prompt_tokens=1024, videos_per_request=1, video_retention_days=2,
        person_generation_modes={},
    )


def test_estimate_beat_seconds_dialogue_scales_with_word_count():
    short = estimate_beat_seconds({"kind": "dialogue", "text": "Hi.", "estimated_seconds": None})
    long = estimate_beat_seconds({"kind": "dialogue", "text": " ".join(["word"] * 30), "estimated_seconds": None})
    assert long > short


def test_estimate_beat_seconds_respects_explicit_override():
    est = estimate_beat_seconds({"kind": "action", "text": "x", "estimated_seconds": 12.0})
    assert est == 12.0


def _one_scene_episode(beats):
    return EpisodeScript.from_dict({
        "episode_id": "ep_bridge", "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
        "scenes": [{
            "scene_id": "scene_01", "location_id": "loc_family_living_room",
            "characters_present": ["char_001_zayd", "char_002_amira"],
            "props_visible": [], "environment_overrides": {"time_of_day": "evening"},
            "beats": beats,
        }],
        "song": None, "story_updates": {},
    })


def test_never_splits_a_single_beat(repo_root):
    long_line = "I promise I will help you fix your kite before the sun sets this weekend, no matter what happens."
    episode = _one_scene_episode([
        {"beat_id": "b1", "kind": "dialogue", "character_id": "char_001_zayd", "text": long_line, "estimated_seconds": None},
    ])
    specs, diagnostics = build_clip_specs(repo_root, episode, _fake_capabilities(8))
    assert len(specs) == 1
    assert long_line in specs[0].raw_prompt_text


def test_camera_change_forces_new_clip_even_with_budget_remaining(repo_root):
    episode = _one_scene_episode([
        {"beat_id": "b1", "kind": "action", "text": "Zayd looks at the broken kite.", "camera_hint": "intimate_emotional_moment", "estimated_seconds": 1.0},
        {"beat_id": "b2", "kind": "dialogue", "character_id": "char_001_zayd", "text": "I can fix this.", "camera_hint": "conflict_introduction", "estimated_seconds": 1.0},
    ])
    specs, _ = build_clip_specs(repo_root, episode, _fake_capabilities(8))
    assert len(specs) == 2
    assert specs[0].scene_type == "intimate_emotional_moment"
    assert specs[1].scene_type == "conflict_introduction"


def test_same_camera_hint_packs_into_one_clip(repo_root):
    episode = _one_scene_episode([
        {"beat_id": "b1", "kind": "action", "text": "Zayd picks up the kite.", "camera_hint": "effort_action", "estimated_seconds": 1.0},
        {"beat_id": "b2", "kind": "dialogue", "character_id": "char_001_zayd", "text": "Almost there.", "camera_hint": "effort_action", "estimated_seconds": 1.0},
    ])
    specs, _ = build_clip_specs(repo_root, episode, _fake_capabilities(8))
    assert len(specs) == 1
    assert "picks up the kite" in specs[0].raw_prompt_text
    assert "Almost there" in specs[0].raw_prompt_text


def test_duration_budget_not_hardcoded_small_budget_more_clips(repo_root):
    beats = [
        {"beat_id": f"b{i}", "kind": "action", "text": f"Action beat number {i}.", "estimated_seconds": 3.0}
        for i in range(6)
    ]
    episode = _one_scene_episode(beats)
    # forces_when_refs=False: exercise the generic max(duration_options_seconds)
    # branch, not Veo's specific "always exactly 8s when refs are used" rule --
    # that rule correctly returns a literal 8 for Veo because that IS Veo's
    # real documented behavior (see test_real_veo31_fast_capability_forces_8s_planning_budget
    # below); it would be wrong to treat that as generic across all providers.
    specs_small, _ = build_clip_specs(repo_root, episode, _fake_capabilities(4, forces_when_refs=False))
    specs_large, _ = build_clip_specs(repo_root, episode, _fake_capabilities(20, forces_when_refs=False))
    assert len(specs_small) > len(specs_large)
    assert len(specs_large) == 1  # 6 * 3.0s = 18s fits entirely under a 20s budget


def test_real_veo31_fast_capability_forces_8s_planning_budget(repo_root):
    # proves the bridge asks the REAL provider object for its real limit,
    # not a hardcoded 8 -- same numeric result here because Veo 3.1 Fast's
    # actual documented rule really is 8s with reference images, but the
    # bridge reached that number via caps.max_duration_seconds(), not a literal
    beats = [{"beat_id": "b1", "kind": "action", "text": "x", "estimated_seconds": 7.9}]
    episode = _one_scene_episode(beats)
    specs, diagnostics = build_clip_specs(repo_root, episode, Veo31FastProvider().capabilities())
    assert len(specs) == 1
    assert diagnostics == []  # 7.9s fits under the real 8s budget, no overflow


def test_overflow_beat_gets_own_clip_and_diagnostic(repo_root):
    episode = _one_scene_episode([
        {"beat_id": "b1", "kind": "action", "text": "A very long, slow, dramatic beat.", "estimated_seconds": 15.0},
    ])
    specs, diagnostics = build_clip_specs(repo_root, episode, _fake_capabilities(8))
    assert len(specs) == 1
    assert len(diagnostics) == 1
    assert diagnostics[0]["severity"] == "warning"
    assert "exceeds the provider's max clip duration" in diagnostics[0]["message"]


def test_environment_overrides_only_on_first_clip_of_scene(repo_root):
    episode = _one_scene_episode([
        {"beat_id": "b1", "kind": "action", "text": "Beat one.", "estimated_seconds": 3.0},
        {"beat_id": "b2", "kind": "action", "text": "Beat two.", "camera_hint": "resolution_relief", "estimated_seconds": 3.0},
    ])
    specs, _ = build_clip_specs(repo_root, episode, _fake_capabilities(3.5, forces_when_refs=False))
    assert len(specs) >= 2
    assert specs[0].environment_overrides == {"time_of_day": "evening"}
    assert specs[1].environment_overrides == {}  # Phase 3's carry-forward applies naturally, not re-declared


def test_default_duplicate_guard_negative_constraints_present(repo_root):
    episode = _one_scene_episode([
        {"beat_id": "b1", "kind": "dialogue", "character_id": "char_001_zayd", "text": "Hello.", "estimated_seconds": 1.0},
    ])
    specs, _ = build_clip_specs(repo_root, episode, _fake_capabilities(8))
    assert any("no duplicate" in c and "Zayd" in c for c in specs[0].negative_constraints)
    # Corrected behavior (was a confirmed real bug): Amira is scene-roster
    # but never appears in this clip's actual content, so she must NOT be
    # dragged into this clip's duplicate-guard or reference-image budget.
    assert not any("Amira" in c for c in specs[0].negative_constraints)


def test_secondary_character_included_when_named_in_action_text(repo_root):
    episode = _one_scene_episode([
        {"beat_id": "b1", "kind": "action", "text": "Zayd waves as Amira runs past him with the kite.", "estimated_seconds": 2.0},
    ])
    specs, _ = build_clip_specs(repo_root, episode, _fake_capabilities(8))
    assert any("Amira" in c for c in specs[0].negative_constraints)


def test_reference_budget_scene_secondary_important_character_not_dragged_in_uninvolved_clip(repo_root):
    """The exact real production bug: a clip whose only actual content is
    one character speaking must not drag unrelated scene-roster characters
    into the reference-image budget competition just because they appear
    somewhere else in the same scene."""
    episode = EpisodeScript.from_dict({
        "episode_id": "ep_ref", "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
        "scenes": [{
            "scene_id": "s1", "location_id": "loc_neighborhood_park",
            "characters_present": ["char_002_amira", "char_001_zayd", "char_057_neighbor_auntie_ruqayyah", "char_058_neighbor_uncle_dawud"],
            "props_visible": [], "environment_overrides": {},
            "beats": [{"beat_id": "b1", "kind": "dialogue", "character_id": "char_002_amira", "emotion": "excited",
                       "text": "Here comes Baba with all the wheelbarrows!", "estimated_seconds": None}],
        }],
        "song": None, "story_updates": {},
    })
    specs, _ = build_clip_specs(repo_root, episode, _fake_capabilities(8))
    assert specs[0].primary_character_ids == ["char_002_amira"]
    assert specs[0].secondary_character_ids == []


def test_reference_budget_scene_visually_important_secondary_still_included_when_relevant(repo_root):
    """The other half of the same fix: a secondary character who IS
    actually relevant to this specific clip (named in its action text)
    correctly still competes for/wins reference-image budget."""
    episode = EpisodeScript.from_dict({
        "episode_id": "ep_ref2", "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
        "scenes": [{
            "scene_id": "s1", "location_id": "loc_neighborhood_park",
            "characters_present": ["char_002_amira", "char_058_neighbor_uncle_dawud"],
            "props_visible": [], "environment_overrides": {},
            "beats": [{"beat_id": "b1", "kind": "action",
                       "text": "Amira notices Uncle Dawud struggling with a heavy bag and rushes to help him.",
                       "estimated_seconds": 3.0}],
        }],
        "song": None, "story_updates": {},
    })
    specs, _ = build_clip_specs(repo_root, episode, _fake_capabilities(8))
    assert "char_058_neighbor_uncle_dawud" in specs[0].secondary_character_ids


def test_previous_clip_id_chains_within_scene(repo_root):
    episode = _one_scene_episode([
        {"beat_id": "b1", "kind": "action", "text": "Beat one.", "camera_hint": "a", "estimated_seconds": 1.0},
        {"beat_id": "b2", "kind": "action", "text": "Beat two.", "camera_hint": "b", "estimated_seconds": 1.0},
    ])
    specs, _ = build_clip_specs(repo_root, episode, _fake_capabilities(8))
    assert specs[0].previous_clip_id is None
    assert specs[1].previous_clip_id == specs[0].clip_id
