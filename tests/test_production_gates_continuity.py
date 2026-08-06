import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.authoring.schemas import EpisodeScript
from tools.production_gates.continuity_gate import continuity_gate_check


def _ep(episode_id, characters, location_id, story_updates=None):
    return EpisodeScript.from_dict({
        "episode_id": episode_id, "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
        "scenes": [{"scene_id": "s1", "location_id": location_id, "characters_present": characters,
                    "props_visible": [], "environment_overrides": {},
                    "beats": [{"beat_id": "b1", "kind": "action", "text": "x", "estimated_seconds": 3.0}]}],
        "song": None, "story_updates": story_updates or {},
    })


def test_valid_season_passes(repo_root):
    episodes = [
        _ep("cg_ep01", ["char_001_zayd"], "loc_family_living_room",
            {"new_threads": [{"kind": "promise", "description": "a promise", "involved_characters": ["char_001_zayd"]}]}),
        _ep("cg_ep02", ["char_001_zayd"], "loc_family_living_room",
            {"referenced_thread_ids": ["thread_cg_ep01_promise_0"]}),
    ]
    result = continuity_gate_check(repo_root, "cg_season1", episodes)
    assert result["status"] == "PASS"


def test_thread_referenced_before_created_blocked(repo_root):
    episodes = [
        _ep("cg_ep01", ["char_001_zayd"], "loc_family_living_room",
            {"referenced_thread_ids": ["thread_cg_ep02_promise_0"]}),  # references a thread from the FUTURE
        _ep("cg_ep02", ["char_001_zayd"], "loc_family_living_room",
            {"new_threads": [{"kind": "promise", "description": "a promise", "involved_characters": ["char_001_zayd"]}]}),
    ]
    result = continuity_gate_check(repo_root, "cg_season2", episodes)
    assert result["status"] == "BLOCKED"
    assert any(f["issue"] == "thread_referenced_before_created" for f in result["findings"])


def test_thread_never_created_at_all_blocked(repo_root):
    episodes = [_ep("cg_ep01", ["char_001_zayd"], "loc_family_living_room",
                     {"resolved_thread_ids": ["thread_that_never_existed"]})]
    result = continuity_gate_check(repo_root, "cg_season3", episodes)
    assert result["status"] == "BLOCKED"


def test_invalid_character_id_anywhere_in_season_blocked(repo_root):
    episodes = [
        _ep("cg_ep01", ["char_001_zayd"], "loc_family_living_room"),
        _ep("cg_ep02", ["char_999_fake"], "loc_family_living_room"),  # invalid, buried in episode 2
    ]
    result = continuity_gate_check(repo_root, "cg_season4", episodes)
    assert result["status"] == "BLOCKED"
    assert any(f.get("invalid_id") == "char_999_fake" and f.get("episode_id") == "cg_ep02" for f in result["findings"])


def test_invalid_environment_id_anywhere_in_season_blocked(repo_root):
    episodes = [_ep("cg_ep01", ["char_001_zayd"], "loc_999_fake")]
    result = continuity_gate_check(repo_root, "cg_season5", episodes)
    assert result["status"] == "BLOCKED"


def test_duplicate_thread_declaration_is_warning_not_blocker(repo_root):
    episodes = [
        _ep("cg_ep01", ["char_001_zayd"], "loc_family_living_room",
            {"new_threads": [{"kind": "lesson", "description": "Be kind.", "involved_characters": ["char_001_zayd"]}]}),
        _ep("cg_ep02", ["char_001_zayd"], "loc_family_living_room",
            {"new_threads": [{"kind": "lesson", "description": "Be kind.", "involved_characters": ["char_001_zayd"]}]}),
    ]
    result = continuity_gate_check(repo_root, "cg_season6", episodes)
    # a soft duplicate signal must not block the season by itself
    assert result["status"] == "PASS"
    assert any(f["issue"] == "possible_duplicate_thread" and f["severity"] == "warning" for f in result["findings"])


def test_empty_season_passes_trivially(repo_root):
    result = continuity_gate_check(repo_root, "cg_season7", [])
    assert result["status"] == "PASS"


def test_result_persisted_as_real_evidence_file(isolated_root):
    episodes = [_ep("cg_ep01", ["char_001_zayd"], "loc_family_living_room")]
    continuity_gate_check(isolated_root, "cg_season_persist", episodes)
    path = isolated_root / "continuity" / "continuity_gate" / "cg_season_persist.json"
    assert path.exists()


# Regression tests for the real false-PASS bug found in production (Arena
# transcript + independent audit, confirmed reproducible before fixing).
def test_real_bug_correct_global_thread_id_no_longer_false_blocked(repo_root):
    """The gate used to re-simulate thread-ID assignment with a
    PER-EPISODE index, diverging from StoryStateRepo's real GLOBAL
    running-count formula starting at episode 2. A reference using the
    real, correct global ID used to be wrongly rejected."""
    ep1 = _ep("ep01", ["char_001_zayd"], "loc_family_living_room",
              {"new_threads": [{"kind": "goal", "description": f"d{i}", "involved_characters": ["char_001_zayd"]}
                                for i in range(4)]})
    ep2 = _ep("ep02", ["char_001_zayd"], "loc_family_living_room",
              {"new_threads": [{"kind": "lesson", "description": "d5", "involved_characters": ["char_001_zayd"]}]})
    ep3 = _ep("ep03", ["char_001_zayd"], "loc_family_living_room",
              {"resolved_thread_ids": ["thread_ep02_lesson_4"]})  # the REAL global-index id
    result = continuity_gate_check(repo_root, "cg_real_bug1", [ep1, ep2, ep3])
    assert result["status"] == "PASS"


def test_real_bug_wrong_per_episode_id_now_correctly_blocked(repo_root):
    """The inverse: the WRONG per-episode-local id that the old buggy
    gate would have accepted (and that Arena's transcript shows it was
    forced to rewrite its content to match) must now be rejected, since
    it does not correspond to anything the real StoryStateRepo produces."""
    ep1 = _ep("ep01", ["char_001_zayd"], "loc_family_living_room",
              {"new_threads": [{"kind": "goal", "description": f"d{i}", "involved_characters": ["char_001_zayd"]}
                                for i in range(4)]})
    ep2 = _ep("ep02", ["char_001_zayd"], "loc_family_living_room",
              {"new_threads": [{"kind": "lesson", "description": "d5", "involved_characters": ["char_001_zayd"]}]})
    ep3 = _ep("ep03", ["char_001_zayd"], "loc_family_living_room",
              {"resolved_thread_ids": ["thread_ep02_lesson_0"]})  # the WRONG per-episode-local id
    result = continuity_gate_check(repo_root, "cg_real_bug2", [ep1, ep2, ep3])
    assert result["status"] == "BLOCKED"
    assert any(f["thread_id"] == "thread_ep02_lesson_0" for f in result["findings"])


def test_gate_never_touches_the_caller_season_story_state(isolated_root):
    """The fix runs a real StoryStateRepo internally -- confirm it uses
    an isolated temp directory and never writes into the caller's own
    continuity/story_state/, which would be a real, serious side effect
    for a function whose entire job is read-only validation."""
    episodes = [_ep("cg_ep01", ["char_001_zayd"], "loc_family_living_room",
                     {"new_threads": [{"kind": "goal", "description": "d", "involved_characters": ["char_001_zayd"]}]})]
    continuity_gate_check(isolated_root, "cg_isolation_check", episodes)
    # the gate's internal dry-run must not leave any trace in the real season's story_state
    real_story_state = isolated_root / "continuity" / "story_state" / "cg_isolation_check.json"
    assert not real_story_state.exists()


def test_real_bug_duplicate_character_in_involved_characters_flagged(repo_root):
    """Exact real production example: a running_joke thread meant to
    involve Nuri AND Barq the kitten, but both entries pointed at
    char_006_nuri -- registry validation alone can't catch this since
    the ID itself is valid."""
    ep = _ep("cg_ep_nuri", ["char_006_nuri"], "loc_family_living_room", {
        "new_threads": [{"kind": "running_joke", "description": "Nuri the cat and Barq the kitten play together",
                          "involved_characters": ["char_006_nuri", "char_006_nuri"]}],
    })
    result = continuity_gate_check(repo_root, "cg_nuri_season", [ep])
    assert result["status"] == "PASS"  # a warning, not a block -- the IDs are individually valid
    assert any(f["issue"] == "duplicate_character_in_thread" and f["severity"] == "warning"
               for f in result["findings"])
