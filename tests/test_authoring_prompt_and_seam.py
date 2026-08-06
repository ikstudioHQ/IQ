import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.authoring.author_provider import build_episode_prompt, build_season_concept_prompt
from tools.authoring.manual_author_seam import (
    load_authored_episode,
    load_season_concept,
    register_authored_episode,
    register_season_concept,
    write_episode_author_request,
    write_season_concept_request,
)
from tools.authoring.story_state import StoryStateRepo


def test_episode_prompt_includes_real_character_data(repo_root):
    prompt = build_episode_prompt(
        repo_root, episode_id="ep01", season_id="season_p", theme="honesty",
        language="English", target_age="5-8", premise="Zayd finds a lost toy.",
        cast_character_ids=["char_001_zayd", "char_002_amira"],
        location_id="loc_family_living_room", episode_duration_minutes=10,
    )
    assert "Zayd" in prompt
    assert "Amira" in prompt
    assert "loc_family_living_room" in prompt
    assert "CONTENT RESTRICTIONS" in prompt


def test_episode_prompt_includes_real_safety_constraints(repo_root):
    prompt = build_episode_prompt(
        repo_root, episode_id="ep01", season_id="season_p2", theme="honesty",
        language="English", target_age="5-8", premise="test",
        cast_character_ids=["char_001_zayd"], location_id=None, episode_duration_minutes=10,
    )
    # real category names from phase2/data/safety/*.json should appear, not invented ones
    assert "Violence" in prompt or "violence" in prompt.lower()


def test_episode_prompt_includes_open_story_threads(isolated_root):
    StoryStateRepo(isolated_root).apply_episode_updates("season_p3", "ep01", {
        "new_threads": [{"kind": "promise", "description": "Zayd promised to fix the kite.",
                          "involved_characters": ["char_001_zayd"]}],
    })
    prompt = build_episode_prompt(
        isolated_root, episode_id="ep02", season_id="season_p3", theme="honesty",
        language="English", target_age="5-8", premise="test",
        cast_character_ids=["char_001_zayd"], location_id=None, episode_duration_minutes=10,
    )
    assert "fix the kite" in prompt
    assert "OPEN STORY THREADS" in prompt


def test_season_concept_prompt_shape():
    prompt = build_season_concept_prompt(
        theme="kindness", episode_count=30, episode_duration_minutes=10,
        language="English", target_age="5-8",
    )
    assert "30-episode" in prompt
    assert "kindness" in prompt


def test_write_and_register_episode_round_trip(isolated_root):
    path = write_episode_author_request(
        isolated_root, episode_id="ep01", season_id="season_seam", theme="honesty",
        language="English", target_age="5-8", premise="test premise",
        cast_character_ids=["char_001_zayd"], location_id=None, episode_duration_minutes=10,
    )
    assert path.exists()
    assert "test premise" in path.read_text()

    episode_data = {
        "episode_id": "ep01", "title": "The Lost Toy", "theme": "honesty",
        "language": "English", "target_age": "5-8",
        "scenes": [], "song": None,
        "story_updates": {"new_threads": [{"kind": "goal", "description": "test goal",
                                            "involved_characters": ["char_001_zayd"]}]},
    }
    register_authored_episode(isolated_root, "season_seam", episode_data)

    loaded = load_authored_episode(isolated_root, "ep01")
    assert loaded.title == "The Lost Toy"

    state = StoryStateRepo(isolated_root).load("season_seam")
    assert len(state.threads) == 1


def test_register_authored_episode_rejects_malformed_data(isolated_root):
    # missing required fields should raise, not silently produce a broken episode
    try:
        register_authored_episode(isolated_root, "season_bad", {"title": "no episode_id"})
        assert False, "should have raised"
    except TypeError:
        pass


def test_season_concept_round_trip(isolated_root):
    write_season_concept_request(
        isolated_root, season_id="season_concept1", theme="kindness", episode_count=5,
        episode_duration_minutes=10, language="English", target_age="5-8",
    )
    concept_data = {
        "season_id": "season_concept1", "theme": "kindness", "language": "English",
        "target_age": "5-8", "episode_count": 5, "episode_duration_minutes": 10,
        "premises": [{"episode_id": "ep01", "title": "t", "premise": "p", "arc_position": "opener"}],
    }
    register_season_concept(isolated_root, concept_data)
    loaded = load_season_concept(isolated_root, "season_concept1")
    assert loaded.episode_count == 5
    assert len(loaded.premises) == 1


def test_load_missing_episode_returns_none(isolated_root):
    assert load_authored_episode(isolated_root, "no_such_episode") is None
