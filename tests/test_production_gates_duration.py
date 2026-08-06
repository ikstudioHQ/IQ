import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.authoring.schemas import EpisodeScript
from tools.production_gates.duration_gate import build_expansion_request, duration_gate_check
from tools.providers.base import ProviderCapabilities
from tools.providers.veo31_fast import Veo31FastProvider


def _episode_with_n_beats(n, episode_id="dur_test"):
    beats = [
        {"beat_id": f"b{i}", "kind": "action", "text": f"Something happens, part {i}.", "estimated_seconds": 3.0}
        for i in range(n)
    ]
    return EpisodeScript.from_dict({
        "episode_id": episode_id, "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
        "scenes": [{"scene_id": "s1", "location_id": "loc_family_living_room",
                    "characters_present": ["char_001_zayd"], "props_visible": [], "environment_overrides": {},
                    "beats": beats}],
        "song": None, "story_updates": {},
    })


# 10-minute request producing materially short content -- the exact real bug
def test_10min_request_with_short_content_fails_gate(repo_root):
    episode = _episode_with_n_beats(5)  # ~5 clips * 8s = 40s, nowhere near 600s
    result = duration_gate_check(repo_root, episode, Veo31FastProvider().capabilities(), requested_minutes=10)
    assert result["status"] == "TOO_SHORT"
    assert result["clip_count"] < 10
    assert result["deviation_ratio"] < -0.15


# Different requested episode durations
def test_different_requested_durations_produce_different_verdicts(repo_root):
    episode = _episode_with_n_beats(20)
    short_target = duration_gate_check(repo_root, episode, Veo31FastProvider().capabilities(), requested_minutes=1)
    long_target = duration_gate_check(repo_root, episode, Veo31FastProvider().capabilities(), requested_minutes=30)
    # same content, same provider -- only the requested target changed, so
    # a small target should pass (or run long) while a huge target must
    # come back short, proving the verdict tracks the request, not the content
    assert short_target["status"] in ("PASS", "TOO_LONG")
    assert long_target["status"] == "TOO_SHORT"


# Different provider clip-duration capabilities -- never hardcoded
def test_different_provider_capabilities_change_clip_count_needed(repo_root):
    fake_caps_4s = ProviderCapabilities(
        provider_id="fake4", model_id="fake4", max_reference_images=3,
        supports_reference_images=True, supports_image_to_video=True,
        supports_last_frame_interpolation=True, supports_video_extension=True,
        duration_options_seconds=[4], duration_forced_to_8_when=[],
        resolution_options=["720p"], aspect_ratios=["16:9"], frame_rate_fps=24,
        max_prompt_tokens=1024, videos_per_request=1, video_retention_days=2,
        person_generation_modes={},
    )
    episode = _episode_with_n_beats(20)
    result_4s = duration_gate_check(repo_root, episode, fake_caps_4s, requested_minutes=1)
    result_8s = duration_gate_check(repo_root, episode, Veo31FastProvider().capabilities(), requested_minutes=1)
    # same content, different provider clip length -> different planned_seconds
    assert result_4s["provider_clip_seconds"] == 4
    assert result_8s["provider_clip_seconds"] == 8
    # different clip-duration budgets change how many beats pack per clip,
    # so the resulting clip COUNT differs even for identical story content --
    # this is the thing that must never be hardcoded, and isn't
    assert result_4s["clip_count"] != result_8s["clip_count"]


# Duration repair without filler -- the expansion request explicitly forbids padding
def test_expansion_request_explicitly_forbids_padding(repo_root):
    episode = _episode_with_n_beats(5)
    result = duration_gate_check(repo_root, episode, Veo31FastProvider().capabilities(), requested_minutes=10)
    prompt = build_expansion_request(repo_root, episode, result)
    assert "Do NOT pad" in prompt
    assert "repeated dialogue" in prompt
    assert "EXPAND" in prompt


def test_too_long_produces_condense_request_not_blind_truncation(repo_root):
    episode = _episode_with_n_beats(200)  # way over any reasonable target
    result = duration_gate_check(repo_root, episode, Veo31FastProvider().capabilities(), requested_minutes=1)
    assert result["status"] == "TOO_LONG"
    prompt = build_expansion_request(repo_root, episode, result)
    assert "CONDENSE" in prompt
    assert "Do NOT blindly truncate" in prompt


def test_within_tolerance_passes(repo_root):
    from tools.production_gates.duration_gate import measure_planned_duration
    episode = _episode_with_n_beats(75)
    measured = measure_planned_duration(repo_root, episode, Veo31FastProvider().capabilities())
    # derive the target from what this content actually plans to, rather
    # than assuming a beat-to-clip ratio -- proves the PASS path works
    # without repeating the earlier wrong assumption that N beats = N clips
    target_minutes = measured["planned_seconds"] / 60
    result = duration_gate_check(repo_root, episode, Veo31FastProvider().capabilities(), requested_minutes=target_minutes)
    assert result["status"] == "PASS"


def test_gate_result_persisted_as_real_evidence_file(isolated_root):
    episode = _episode_with_n_beats(5)
    duration_gate_check(isolated_root, episode, Veo31FastProvider().capabilities(), requested_minutes=10)
    path = isolated_root / "continuity" / "duration_gate" / "dur_test.json"
    assert path.exists()
