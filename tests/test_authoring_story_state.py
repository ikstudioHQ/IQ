import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.authoring.story_state import StoryStateRepo


def test_new_state_has_no_threads(isolated_root):
    repo = StoryStateRepo(isolated_root)
    state = repo.load("season_test1")
    assert state.threads == []
    assert state.open_threads() == []


def test_new_thread_created_and_open(isolated_root):
    repo = StoryStateRepo(isolated_root)
    repo.apply_episode_updates("season_test2", "ep01", {
        "new_threads": [{"kind": "promise", "description": "Zayd promises to help fix Amira's kite.",
                          "involved_characters": ["char_001_zayd", "char_002_amira"]}],
    })
    state = repo.load("season_test2")
    assert len(state.threads) == 1
    assert state.threads[0]["status"] == "open"
    assert state.threads[0]["kind"] == "promise"
    assert state.threads[0]["origin_episode_id"] == "ep01"


def test_thread_resolution_across_episodes(isolated_root):
    repo = StoryStateRepo(isolated_root)
    repo.apply_episode_updates("season_test3", "ep01", {
        "new_threads": [{"kind": "promise", "description": "Zayd promises to help fix Amira's kite.",
                          "involved_characters": ["char_001_zayd", "char_002_amira"]}],
    })
    state = repo.load("season_test3")
    thread_id = state.threads[0]["thread_id"]

    repo.apply_episode_updates("season_test3", "ep02", {
        "resolved_thread_ids": [thread_id],
        "resolution_notes": {thread_id: "Zayd fixed the kite at the park."},
    })
    state2 = repo.load("season_test3")
    assert state2.threads[0]["status"] == "resolved"
    assert state2.threads[0]["resolved_episode_id"] == "ep02"
    assert "fixed the kite" in state2.threads[0]["resolution_note"]
    assert state2.open_threads() == []


def test_referenced_thread_increments_callback_count(isolated_root):
    repo = StoryStateRepo(isolated_root)
    repo.apply_episode_updates("season_test4", "ep01", {
        "new_threads": [{"kind": "running_joke", "description": "Zayd always ties bad knots.",
                          "involved_characters": ["char_001_zayd"]}],
    })
    thread_id = repo.load("season_test4").threads[0]["thread_id"]

    repo.apply_episode_updates("season_test4", "ep02", {"referenced_thread_ids": [thread_id]})
    repo.apply_episode_updates("season_test4", "ep03", {"referenced_thread_ids": [thread_id]})
    state = repo.load("season_test4")
    assert state.threads[0]["callback_count"] == 2
    assert state.threads[0]["status"] == "open"  # referencing doesn't resolve it


def test_threads_involving_filters_by_character(isolated_root):
    repo = StoryStateRepo(isolated_root)
    repo.apply_episode_updates("season_test5", "ep01", {
        "new_threads": [
            {"kind": "goal", "description": "Amira wants to learn a new surah.", "involved_characters": ["char_002_amira"]},
            {"kind": "secret", "description": "Zayd hides that he broke the lamp.", "involved_characters": ["char_001_zayd"]},
        ],
    })
    state = repo.load("season_test5")
    amira_threads = state.threads_involving("char_002_amira")
    assert len(amira_threads) == 1
    assert amira_threads[0]["kind"] == "goal"


def test_emotional_notes_logged(isolated_root):
    repo = StoryStateRepo(isolated_root)
    repo.apply_episode_updates("season_test6", "ep01", {
        "emotional_notes": [{"character_id": "char_001_zayd", "note": "Zayd feels guilty about breaking the lamp."}],
    })
    state = repo.load("season_test6")
    assert len(state.emotional_arc_log) == 1
    assert state.emotional_arc_log[0]["character_id"] == "char_001_zayd"


def test_missing_story_updates_fields_are_not_errors(isolated_root):
    repo = StoryStateRepo(isolated_root)
    # empty dict -- an episode that declares nothing new must not raise
    state = repo.apply_episode_updates("season_test7", "ep01", {})
    assert state.threads == []
