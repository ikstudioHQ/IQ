import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.authoring.schemas import EpisodeScript
from tools.production_gates.song_gate import count_songs_in_season, song_gate_check


def _ep_with_song(song, episode_id="song_test"):
    return EpisodeScript.from_dict({
        "episode_id": episode_id, "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
        "scenes": [], "story_updates": {}, "song": song,
    })


def test_real_bug_song_included_with_only_theme_no_lyrics_blocked(repo_root):
    episode = _ep_with_song({
        "included": True, "reason": "emotional peak",
        "lyrics_theme": "After every storm, the garden drinks the rain and grows stronger.",
        "placement_scene_id": "s07",
    })
    result = song_gate_check(repo_root, episode)
    assert result["status"] == "BLOCKED"
    assert result["findings"][0]["issue"] == "song_included_without_lyrics"


def test_song_not_included_never_checked(repo_root):
    episode = _ep_with_song({"included": False, "reason": "no emotional peak here"})
    result = song_gate_check(repo_root, episode)
    assert result["status"] == "PASS"


def test_lyrics_too_short_blocked(repo_root):
    episode = _ep_with_song({
        "included": True, "reason": "peak", "lyrics_theme": "theme",
        "lyrics": "A short song line only.",
    })
    result = song_gate_check(repo_root, episode)
    assert result["status"] == "BLOCKED"
    assert result["findings"][0]["issue"] == "song_lyrics_too_short"


def test_lyrics_copied_from_theme_blocked(repo_root):
    theme = "A description of the song that someone lazily copied into the lyrics field instead of writing real verses."
    episode = _ep_with_song({
        "included": True, "reason": "peak", "lyrics_theme": theme, "lyrics": theme,
    })
    result = song_gate_check(repo_root, episode)
    assert result["status"] == "BLOCKED"
    assert result["findings"][0]["issue"] == "song_lyrics_same_as_theme"


def test_real_substantial_lyrics_pass(repo_root):
    episode = _ep_with_song({
        "included": True, "reason": "peak", "lyrics_theme": "theme",
        "lyrics": (
            "After the rain, the garden stands tall,\n"
            "Every seed remembers how to grow.\n"
            "We planted with love, we watered with care,\n"
            "And now something beautiful blooms right here."
        ),
    })
    result = song_gate_check(repo_root, episode)
    assert result["status"] == "PASS"


def test_count_songs_in_season_only_counts_real_lyrics(repo_root):
    ep_no_lyrics = EpisodeScript.from_dict({
        "episode_id": "e1", "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
        "scenes": [], "story_updates": {},
        "song": {"included": True, "reason": "r", "lyrics_theme": "t"},
    })
    ep_real = EpisodeScript.from_dict({
        "episode_id": "e2", "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
        "scenes": [], "story_updates": {},
        "song": {"included": True, "reason": "r", "lyrics_theme": "t",
                 "lyrics": "Real verses here with enough words to count as an actual written song, not a placeholder."},
    })
    ep_none = EpisodeScript.from_dict({
        "episode_id": "e3", "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
        "scenes": [], "story_updates": {}, "song": None,
    })
    assert count_songs_in_season([ep_no_lyrics, ep_real, ep_none]) == 1
