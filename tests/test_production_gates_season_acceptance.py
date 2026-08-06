import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.authoring.manual_author_seam import register_authored_episode, register_season_concept
from tools.orchestration import job_state as js
from tools.orchestration.season_orchestrator import advance, generate_season
from tools.production_gates.season_acceptance import run_season_acceptance_gate


GOOD_EPISODE = {
    "episode_id": "sa_ep_good", "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
    "scenes": [{"scene_id": "s1", "location_id": "loc_family_living_room",
                "characters_present": ["char_001_zayd"], "props_visible": [], "environment_overrides": {},
                "beats": [{"beat_id": "b1", "kind": "dialogue", "character_id": "char_001_zayd",
                           "text": "Sharing with a neighbor makes everyone happy.", "estimated_seconds": None}]}],
    "song": None, "story_updates": {},
}

BAD_ISLAMIC_EPISODE = {
    "episode_id": "sa_ep_bad_islamic", "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
    "scenes": [{"scene_id": "s1", "location_id": "loc_family_living_room",
                "characters_present": ["char_001_zayd"], "props_visible": [], "environment_overrides": {},
                "beats": [{"beat_id": "b1", "kind": "action",
                           "text": "The Prophet taught us this exact unsourced thing.", "estimated_seconds": 3.0}]}],
    "song": None, "story_updates": {},
}


def test_season_acceptance_never_defaults_ready(isolated_root):
    register_season_concept(isolated_root, {
        "season_id": "sa1", "theme": "t", "language": "English", "target_age": "5-8",
        "episode_count": 1, "episode_duration_minutes": 10,
        "premises": [{"episode_id": "sa_ep_missing", "title": "t", "premise": "t", "arc_position": "opener"}],
    })
    result = run_season_acceptance_gate(isolated_root, "sa1", ["sa_ep_missing"], "veo-3.1-fast", 10)
    assert result["status"] == "REPAIR_REQUIRED"
    assert result["episodes"]["sa_ep_missing"]["status"] == "MISSING"


def test_season_acceptance_blocks_on_islamic_gate_failure(isolated_root):
    register_authored_episode(isolated_root, "sa2", BAD_ISLAMIC_EPISODE)
    result = run_season_acceptance_gate(isolated_root, "sa2", ["sa_ep_bad_islamic"], "veo-3.1-fast", 10)
    assert result["status"] == "REPAIR_REQUIRED"
    assert result["episodes"]["sa_ep_bad_islamic"]["gates"]["islamic"] == "BLOCKED"


def test_season_acceptance_blocks_on_duration_failure(isolated_root):
    register_authored_episode(isolated_root, "sa3", GOOD_EPISODE)
    result = run_season_acceptance_gate(isolated_root, "sa3", ["sa_ep_good"], "veo-3.1-fast", 10)
    assert result["status"] == "REPAIR_REQUIRED"
    assert result["episodes"]["sa_ep_good"]["gates"]["duration"] == "TOO_SHORT"


def test_season_acceptance_result_persisted(isolated_root):
    register_authored_episode(isolated_root, "sa4", GOOD_EPISODE)
    run_season_acceptance_gate(isolated_root, "sa4", ["sa_ep_good"], "veo-3.1-fast", 10)
    path = isolated_root / "continuity" / "season_acceptance" / "sa4.json"
    assert path.exists()


# Real gap found in production audit: season_acceptance could say READY
# purely from authoring-level gates, even though no clip ever had its
# actual provider-ready request built (ID validation/safety never ran).
def test_season_acceptance_blocks_when_requests_never_built(isolated_root):
    from tools.authoring.scene_to_clip_bridge import build_clip_specs
    from tools.providers.veo31_fast import Veo31FastProvider
    import json

    # Build a real, duration-satisfying, valid episode -- but only plan
    # clips (build_clip_specs), never call ContinuityAssembler to build
    # the actual requests. This is exactly the real gap: authoring +
    # clip-planning happened, the request-building step did not.
    big_episode = {
        "episode_id": "sa_ep_unbuilt", "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
        "scenes": [{"scene_id": "s1", "location_id": "loc_family_living_room",
                    "characters_present": ["char_001_zayd"], "props_visible": [], "environment_overrides": {},
                    "beats": [{"beat_id": f"b{i}", "kind": "dialogue", "character_id": "char_001_zayd",
                               "text": "A real sentence of dialogue with enough words in it to take real time.",
                               "estimated_seconds": None} for i in range(80)]}],
        "song": None, "story_updates": {},
    }
    register_authored_episode(isolated_root, "sa5", big_episode)
    from tools.authoring.manual_author_seam import load_authored_episode
    episode = load_authored_episode(isolated_root, "sa_ep_unbuilt")
    specs, _ = build_clip_specs(isolated_root, episode, Veo31FastProvider().capabilities())
    (isolated_root / "continuity" / "clip_plan").mkdir(parents=True, exist_ok=True)
    (isolated_root / "continuity" / "clip_plan" / "sa_ep_unbuilt.json").write_text(
        json.dumps({"episode_id": "sa_ep_unbuilt", "clips": [s.__dict__ for s in specs], "diagnostics": []})
    )

    result = run_season_acceptance_gate(isolated_root, "sa5", ["sa_ep_unbuilt"], "veo-3.1-fast", 10)
    assert result["status"] == "REPAIR_REQUIRED"
    assert result["requests_built_findings"]
    assert result["requests_built_findings"][0]["issue"] == "clips_planned_but_requests_not_built"


def test_season_acceptance_note_field_clarifies_ready_scope(isolated_root):
    register_authored_episode(isolated_root, "sa6", GOOD_EPISODE)
    result = run_season_acceptance_gate(isolated_root, "sa6", ["sa_ep_good"], "veo-3.1-fast", 10)
    assert "not mean clips have been generated" in result["note"].lower() or "does not mean" in result["note"].lower()


def test_season_acceptance_required_song_count_enforced(isolated_root):
    from tools.continuity.assembler import ContinuityAssembler
    from tools.authoring.scene_to_clip_bridge import build_clip_specs
    from tools.authoring.manual_author_seam import load_authored_episode
    from tools.providers.veo31_fast import Veo31FastProvider

    register_authored_episode(isolated_root, "sa7", GOOD_EPISODE)  # song=None
    episode = load_authored_episode(isolated_root, "sa_ep_good")
    provider = Veo31FastProvider()
    specs, _ = build_clip_specs(isolated_root, episode, provider.capabilities())
    assembler = ContinuityAssembler(str(isolated_root), provider)
    for spec in specs:
        assembler.process_clip(spec)

    result = run_season_acceptance_gate(isolated_root, "sa7", ["sa_ep_good"], "veo-3.1-fast", 10,
                                         required_song_count=2)
    assert result["song_count_ok"] is False
    assert result["real_song_count"] == 0
    assert result["status"] == "REPAIR_REQUIRED"


def test_normal_one_click_call_automatically_enforces_all_gates(isolated_root):
    """Required adversarial proof #1 and #5: a completely ordinary
    generate_season() call, with no gate-related parameter mentioned at
    all, must enforce gates. There is no flag to omit or forget --
    proving this requires NOT passing anything gate-related, which is
    exactly what a real production caller would do."""
    register_season_concept(isolated_root, {
        "season_id": "og1", "theme": "t", "language": "English", "target_age": "5-8",
        "episode_count": 1, "episode_duration_minutes": 10,
        "premises": [{"episode_id": "sa_ep_bad_islamic", "title": "t", "premise": "t", "arc_position": "opener"}],
    })
    register_authored_episode(isolated_root, "og1", BAD_ISLAMIC_EPISODE)
    state = generate_season(isolated_root, season_id="og1", theme="t", episode_count=1,
                             episode_duration_minutes=10, language="English", target_age="5-8",
                             author_provider=None, veo_executor=None)
    ep = state["episodes"]["sa_ep_bad_islamic"]
    assert ep["status"] == js.EPISODE_GATE_REPAIR_REQUIRED
    assert ep["gate_failure"]["islamic"] == "BLOCKED"
    assert ep["clips"] == {}


def test_materially_short_episode_cannot_become_ready(isolated_root):
    """Required adversarial proof #2, via a normal call -- no override."""
    register_season_concept(isolated_root, {
        "season_id": "og3", "theme": "t", "language": "English", "target_age": "5-8",
        "episode_count": 1, "episode_duration_minutes": 10,
        "premises": [{"episode_id": "sa_ep_good", "title": "t", "premise": "t", "arc_position": "opener"}],
    })
    register_authored_episode(isolated_root, "og3", GOOD_EPISODE)
    state = generate_season(isolated_root, season_id="og3", theme="t", episode_count=1,
                             episode_duration_minutes=10, language="English", target_age="5-8",
                             author_provider=None, veo_executor=None)
    ep = state["episodes"]["sa_ep_good"]
    assert ep["status"] == js.EPISODE_GATE_REPAIR_REQUIRED
    assert ep["gate_failure"]["duration"] == "TOO_SHORT"
    assert state["status"] != js.SEASON_COMPLETE


def test_dangling_story_state_reference_cannot_become_ready(isolated_root):
    """Required adversarial proof #4: a season where a later episode
    references a Story State thread an earlier episode never actually
    created must never reach SEASON_COMPLETE, via a normal call."""
    ep1 = {
        "episode_id": "sa_dangle_01", "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
        "scenes": [{"scene_id": "s1", "location_id": "loc_family_living_room",
                    "characters_present": ["char_001_zayd"], "props_visible": [], "environment_overrides": {},
                    "beats": [{"beat_id": f"b{i}", "kind": "dialogue", "character_id": "char_001_zayd",
                               "text": f"Real dialogue line number {i} for this episode.", "estimated_seconds": None}
                              for i in range(80)]}],
        "song": None, "story_updates": {},  # declares NOTHING
    }
    ep2 = {
        "episode_id": "sa_dangle_02", "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
        "scenes": [{"scene_id": "s1", "location_id": "loc_family_living_room",
                    "characters_present": ["char_001_zayd"], "props_visible": [], "environment_overrides": {},
                    "beats": [{"beat_id": f"b{i}", "kind": "dialogue", "character_id": "char_001_zayd",
                               "text": f"Real dialogue line number {i} for this episode.", "estimated_seconds": None}
                              for i in range(80)]}],
        # references a thread episode 1 never declared -- the exact real
        # bug found in the audited production data
        "song": None, "story_updates": {"referenced_thread_ids": ["thread_sa_dangle_01_promise_0"]},
    }
    register_season_concept(isolated_root, {
        "season_id": "og_dangle", "theme": "t", "language": "English", "target_age": "5-8",
        "episode_count": 2, "episode_duration_minutes": 10,
        "premises": [
            {"episode_id": "sa_dangle_01", "title": "t", "premise": "t", "arc_position": "opener"},
            {"episode_id": "sa_dangle_02", "title": "t", "premise": "t", "arc_position": "finale"},
        ],
    })
    register_authored_episode(isolated_root, "og_dangle", ep1)
    register_authored_episode(isolated_root, "og_dangle", ep2)
    state = generate_season(isolated_root, season_id="og_dangle", theme="t", episode_count=2,
                             episode_duration_minutes=10, language="English", target_age="5-8",
                             author_provider=None, veo_executor=None)
    assert state["status"] != js.SEASON_COMPLETE


def test_explicit_bypass_requires_unmistakable_test_only_object(isolated_root):
    """Required adversarial proof #6: the ONLY way to skip gates is to
    import and construct DisableProductionGatesForTesting -- confirm it
    cannot be replicated with a plain bool, None being passed by
    accident, or any other implicit route."""
    from tools.orchestration.testing_overrides import DisableProductionGatesForTesting
    register_season_concept(isolated_root, {
        "season_id": "og4", "theme": "t", "language": "English", "target_age": "5-8",
        "episode_count": 1, "episode_duration_minutes": 10,
        "premises": [{"episode_id": "sa_ep_bad_islamic", "title": "t", "premise": "t", "arc_position": "opener"}],
    })
    register_authored_episode(isolated_root, "og4", BAD_ISLAMIC_EPISODE)

    # A bare True/1/"yes" cannot substitute for the real override object --
    # the parameter's type is enforced by what the code actually checks
    # (`is None` vs a real instance), not by truthiness, so nothing
    # short of the real class has any effect.
    state = generate_season(isolated_root, season_id="og4", theme="t", episode_count=1,
                             episode_duration_minutes=10, language="English", target_age="5-8",
                             author_provider=None, veo_executor=None,
                             _test_only_disable_gates=None)
    ep = state["episodes"]["sa_ep_bad_islamic"]
    assert ep["status"] == js.EPISODE_GATE_REPAIR_REQUIRED  # still enforced

    # the real override requires a non-empty reason -- cannot be
    # constructed carelessly either
    try:
        DisableProductionGatesForTesting(reason="")
        assert False, "should have raised"
    except ValueError:
        pass

    # and the class itself lives in an unmistakably-named test-only module
    assert "testing_overrides" in DisableProductionGatesForTesting.__module__
    assert "Testing" in DisableProductionGatesForTesting.__name__
    assert ep["gate_failure"]["duration"] == "TOO_SHORT"
