import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.authoring.schemas import EpisodeScript
from tools.production_gates.islamic_gate import eligible_sources_prompt_block, post_authoring_islamic_check
from tools.production_gates.islamic_sources import is_eligible, load_eligible_sources


def _episode_with_beat(text, episode_id="isl_test", song=None):
    return EpisodeScript.from_dict({
        "episode_id": episode_id, "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
        "scenes": [{"scene_id": "s1", "location_id": "loc_family_living_room",
                    "characters_present": ["char_001_zayd"], "props_visible": [], "environment_overrides": {},
                    "beats": [{"beat_id": "b1", "kind": "action", "text": text, "estimated_seconds": 3.0}]}],
        "song": song, "story_updates": {},
    })


def test_unsourced_hadith_attribution_blocked(repo_root):
    episode = _episode_with_beat("The Prophet taught us that removing harm from the path is charity!")
    result = post_authoring_islamic_check(repo_root, episode)
    assert result["status"] == "BLOCKED"
    assert any(f["issue"] == "unsourced_religious_claim" for f in result["findings"])


def test_nonexistent_source_id_blocked(repo_root):
    episode = _episode_with_beat("The Prophet said something wise (hd_999).")
    result = post_authoring_islamic_check(repo_root, episode)
    assert result["status"] == "BLOCKED"
    assert any(f["issue"] == "ineligible_or_unknown_citation" and f.get("cited_id") == "hd_999" for f in result["findings"])


def test_unreviewed_source_hd_010_blocked(repo_root):
    eligible, reason = is_eligible(repo_root, "hd_010")
    assert eligible is False  # confirm the registry itself still marks this review_required
    episode = _episode_with_beat("Every good deed is charity, smiling is charity (hd_010).")
    result = post_authoring_islamic_check(repo_root, episode)
    assert result["status"] == "BLOCKED"
    assert any(f.get("cited_id") == "hd_010" for f in result["findings"])


def test_unauthorized_dua_blocked(repo_root):
    episode = _episode_with_beat("O Allah, grant our community peace, health, and steadfastness.")
    result = post_authoring_islamic_check(repo_root, episode)
    assert result["status"] == "BLOCKED"
    assert any("dua" in " ".join(f["claim_reasons"]) for f in result["findings"])


def test_religious_content_in_song_lyrics_not_bypassed(repo_root):
    episode = _episode_with_beat(
        "Zayd and Amira sing together.",
        song={"included": True, "reason": "A happy moment.",
              "lyrics_theme": "Tabassumuka fi wajhi akhika sadaqa", "placement_scene_id": "s1"},
    )
    result = post_authoring_islamic_check(repo_root, episode)
    assert result["status"] == "BLOCKED"
    assert any(f["context"] == "song.lyrics_theme" for f in result["findings"])


def test_valid_eligible_source_passes(repo_root):
    eligible = load_eligible_sources(repo_root)
    assert "hd_001" in eligible
    episode = _episode_with_beat("The Prophet said the best of people are those who are best to their families (hd_001).")
    result = post_authoring_islamic_check(repo_root, episode)
    assert result["status"] == "PASS"
    assert result["findings"] == []


def test_ordinary_kindness_dialogue_not_blocked(repo_root):
    episode = _episode_with_beat("Sharing with your neighbor makes everyone feel happy and cared for.")
    result = post_authoring_islamic_check(repo_root, episode)
    assert result["status"] == "PASS"


def test_everyday_islamic_vocabulary_not_over_blocked(repo_root):
    episode = _episode_with_beat("Alhamdulillah! Bismillah, let's start. Insha'Allah we will finish soon.")
    result = post_authoring_islamic_check(repo_root, episode)
    assert result["status"] == "PASS"


def test_gate_never_mutates_review_required_field(repo_root):
    path = repo_root / "phase2" / "data" / "islamic" / "hadith.json"
    before = path.read_text()
    episode = _episode_with_beat("The Prophet taught us something with no source.")
    post_authoring_islamic_check(repo_root, episode)
    after = path.read_text()
    assert before == after


def test_eligible_sources_prompt_never_includes_review_required_entries(repo_root):
    block = eligible_sources_prompt_block(repo_root)
    assert "hd_010" not in block
    assert "hd_001" in block


def test_gate_result_persisted_as_real_evidence_file(isolated_root):
    episode = _episode_with_beat("The Prophet taught us something with no source.", episode_id="isl_persist")
    post_authoring_islamic_check(isolated_root, episode)
    path = isolated_root / "continuity" / "islamic_gate" / "isl_persist.json"
    assert path.exists()
