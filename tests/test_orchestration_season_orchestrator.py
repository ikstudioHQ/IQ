import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.authoring.manual_author_seam import register_authored_episode, register_season_concept
from tools.orchestration import job_state as js
from tools.orchestration.job_state import JobStateRepo
from tools.orchestration.season_orchestrator import advance, generate_season
from tools.orchestration.testing_overrides import DisableProductionGatesForTesting

# All tests in this file exercise resumability, safety-blocking, repair
# caps, and idempotency -- none of them are testing Duration/Islamic/
# Continuity gate behavior (that's test_production_gates_season_acceptance.py's
# job). Explicitly disabling gates here, with a stated reason, is exactly
# the sanctioned test-only mechanism -- not a way to avoid updating these
# fixtures to satisfy gates that were never what these tests were about.
_SKIP_GATES = DisableProductionGatesForTesting(reason="testing orchestrator mechanics unrelated to production gates")


SIMPLE_EPISODE = {
    "episode_id": "ep_o1", "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
    "scenes": [{
        "scene_id": "scene_01", "location_id": "loc_family_living_room",
        "characters_present": ["char_001_zayd"], "props_visible": [], "environment_overrides": {},
        "beats": [{"beat_id": "b1", "kind": "dialogue", "character_id": "char_001_zayd",
                   "text": "Hello there.", "estimated_seconds": None}],
    }],
    "song": None, "story_updates": {},
}

UNSAFE_EPISODE = {
    "episode_id": "ep_o2", "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
    "scenes": [{
        "scene_id": "scene_01", "location_id": "loc_family_living_room",
        "characters_present": ["char_001_zayd"], "props_visible": [], "environment_overrides": {},
        "beats": [{"beat_id": "b1", "kind": "action",
                   "text": "Blood drips from the broken weapons on the floor.", "estimated_seconds": 3.0}],
    }],
    "song": None, "story_updates": {},
}


def test_no_credentials_at_all_waits_honestly_for_external_authoring(isolated_root):
    generate_season(isolated_root, season_id="orch1", theme="t", episode_count=1,
                     episode_duration_minutes=5, language="English", target_age="5-8",
                     author_provider=None, veo_executor=None, _test_only_disable_gates=_SKIP_GATES)
    job = JobStateRepo(isolated_root).load("orch1")
    assert job.status == js.SEASON_WAITING_FOR_EXTERNAL_AUTHORING
    # a real, readable prompt file must exist for a human to act on
    assert (isolated_root / "continuity" / "author_requests" / "orch1" / "season_concept_prompt.txt").exists()


def test_resumes_after_external_authoring_registered(isolated_root):
    generate_season(isolated_root, season_id="orch2", theme="t", episode_count=1,
                     episode_duration_minutes=5, language="English", target_age="5-8",
                     author_provider=None, veo_executor=None, _test_only_disable_gates=_SKIP_GATES)

    register_season_concept(isolated_root, {
        "season_id": "orch2", "theme": "t", "language": "English", "target_age": "5-8",
        "episode_count": 1, "episode_duration_minutes": 5,
        "premises": [{"episode_id": "ep_o1", "title": "t", "premise": "t", "arc_position": "opener"}],
    })
    register_authored_episode(isolated_root, "orch2", SIMPLE_EPISODE)

    state = generate_season(isolated_root, season_id="orch2", theme="t", episode_count=1,
                             episode_duration_minutes=5, language="English", target_age="5-8",
                             author_provider=None, veo_executor=None, _test_only_disable_gates=_SKIP_GATES)
    # clips should now be planned and built (real ContinuityAssembler calls happened),
    # correctly waiting on the external Veo credential -- never faked as generated
    ep = state["episodes"]["ep_o1"]
    assert ep["status"] == "IN_PROGRESS"
    assert len(ep["clips"]) >= 1
    assert all(c["status"] == js.CLIP_WAITING_FOR_EXTERNAL_GENERATION for c in ep["clips"].values())


def test_resume_does_not_recreate_or_reprocess_already_settled_clips(isolated_root):
    register_season_concept(isolated_root, {
        "season_id": "orch3", "theme": "t", "language": "English", "target_age": "5-8",
        "episode_count": 1, "episode_duration_minutes": 5,
        "premises": [{"episode_id": "ep_o1", "title": "t", "premise": "t", "arc_position": "opener"}],
    })
    register_authored_episode(isolated_root, "orch3", SIMPLE_EPISODE)

    state1 = generate_season(isolated_root, season_id="orch3", theme="t", episode_count=1,
                              episode_duration_minutes=5, language="English", target_age="5-8",
                              author_provider=None, veo_executor=None, _test_only_disable_gates=_SKIP_GATES)
    clip_key = next(iter(state1["episodes"]["ep_o1"]["clips"]))
    first_pass_status = state1["episodes"]["ep_o1"]["clips"][clip_key]["status"]

    # Call advance() again directly (simulating a resumed/restarted process)
    state2 = advance(isolated_root, "orch3", author_provider=None, veo_executor=None, _test_only_disable_gates=_SKIP_GATES)
    second_pass_status = state2["episodes"]["ep_o1"]["clips"][clip_key]["status"]
    assert first_pass_status == second_pass_status == js.CLIP_WAITING_FOR_EXTERNAL_GENERATION


def test_unsafe_authored_content_reaches_blocked_state_via_orchestrator(isolated_root):
    register_season_concept(isolated_root, {
        "season_id": "orch4", "theme": "t", "language": "English", "target_age": "5-8",
        "episode_count": 1, "episode_duration_minutes": 5,
        "premises": [{"episode_id": "ep_o2", "title": "t", "premise": "t", "arc_position": "opener"}],
    })
    register_authored_episode(isolated_root, "orch4", UNSAFE_EPISODE)

    state = generate_season(isolated_root, season_id="orch4", theme="t", episode_count=1,
                             episode_duration_minutes=5, language="English", target_age="5-8",
                             author_provider=None, veo_executor=None, _test_only_disable_gates=_SKIP_GATES)
    ep = state["episodes"]["ep_o2"]
    clip = next(iter(ep["clips"].values()))
    assert clip["status"] == js.CLIP_BLOCKED
    assert clip["last_error"]  # a real reason recorded, not a silent block
    assert ep["status"] == "INCOMPLETE"  # a blocked clip must never be reported as a settled success


def test_resume_after_external_generation_registered(isolated_root):
    register_season_concept(isolated_root, {
        "season_id": "orch6", "theme": "t", "language": "English", "target_age": "5-8",
        "episode_count": 1, "episode_duration_minutes": 5,
        "premises": [{"episode_id": "ep_o1", "title": "t", "premise": "t", "arc_position": "opener"}],
    })
    register_authored_episode(isolated_root, "orch6", SIMPLE_EPISODE)
    state = generate_season(isolated_root, season_id="orch6", theme="t", episode_count=1,
                             episode_duration_minutes=5, language="English", target_age="5-8",
                             author_provider=None, veo_executor=None, _test_only_disable_gates=_SKIP_GATES)
    clip_key = next(iter(state["episodes"]["ep_o1"]["clips"]))
    scene_id, clip_id = clip_key.split("/")
    assert state["episodes"]["ep_o1"]["clips"][clip_key]["status"] == js.CLIP_WAITING_FOR_EXTERNAL_GENERATION

    # Simulate a human generating this clip externally and registering it
    # via the existing Phase 3 manual seam -- exactly what a real operator
    # would do without a wired-in Veo credential.
    from tools.continuity.clip_output_registrar import register_clip_output
    from tools.providers.veo31_fast import Veo31FastProvider
    register_clip_output(
        isolated_root, "ep_o1", scene_id, clip_id,
        provider_capabilities=Veo31FastProvider().capabilities(),
        last_frame_path="continuity/frames/ep_o1/fake_frame.jpg",
    )

    state2 = advance(isolated_root, "orch6", author_provider=None, veo_executor=None, _test_only_disable_gates=_SKIP_GATES)
    clip = state2["episodes"]["ep_o1"]["clips"][clip_key]
    # must have picked up the externally-registered output and progressed
    # past WAITING -- either straight to PASSED (clean structural QA) or
    # further along, but never stuck
    assert clip["status"] != js.CLIP_WAITING_FOR_EXTERNAL_GENERATION


def test_repair_attempt_limit_reached_via_orchestrator(isolated_root):
    from tools.continuity.clip_output_registrar import register_clip_output
    from tools.providers.veo31_fast import Veo31FastProvider

    over_budget_episode = {
        "episode_id": "ep_o3", "title": "t", "theme": "t", "language": "English", "target_age": "5-8",
        "scenes": [{
            "scene_id": "scene_01", "location_id": "loc_family_living_room",
            "characters_present": ["char_001_zayd", "char_002_amira", "char_003_ummi_layla", "char_004_baba_ahmad"],
            "props_visible": [], "environment_overrides": {},
            "beats": [{"beat_id": "b1", "kind": "action", "text": "The whole family gathers together.",
                       "estimated_seconds": 3.0}],
        }],
        "song": None, "story_updates": {},
    }
    register_season_concept(isolated_root, {
        "season_id": "orch7", "theme": "t", "language": "English", "target_age": "5-8",
        "episode_count": 1, "episode_duration_minutes": 5,
        "premises": [{"episode_id": "ep_o3", "title": "t", "premise": "t", "arc_position": "opener"}],
    })
    register_authored_episode(isolated_root, "orch7", over_budget_episode)

    caps = Veo31FastProvider().capabilities()
    generate_season(isolated_root, season_id="orch7", theme="t", episode_count=1,
                     episode_duration_minutes=5, language="English", target_age="5-8",
                     author_provider=None, veo_executor=None, _test_only_disable_gates=_SKIP_GATES)
    for _ in range(5):  # more than enough calls to exhaust MAX_REPAIR_ATTEMPTS
        state = advance(isolated_root, "orch7", author_provider=None, veo_executor=None, _test_only_disable_gates=_SKIP_GATES)
        ep = state["episodes"]["ep_o3"]
        clip_key = next(iter(ep["clips"]))
        clip = ep["clips"][clip_key]
        if clip["status"] == js.CLIP_WAITING_FOR_EXTERNAL_GENERATION:
            scene_id, clip_id = clip_key.split("/")
            register_clip_output(isolated_root, "ep_o3", scene_id, clip_id,
                                  provider_capabilities=caps, last_frame_path="continuity/frames/fake.jpg")
        elif clip["status"] in (js.CLIP_REPAIR_REQUIRED, js.CLIP_PASSED):
            break

    final = advance(isolated_root, "orch7", author_provider=None, veo_executor=None, _test_only_disable_gates=_SKIP_GATES)
    final_clip = next(iter(final["episodes"]["ep_o3"]["clips"].values()))
    # with only 3 reference-image slots and 4 characters, this can never
    # fully resolve -- the repair-attempt cap must eventually stop it
    # rather than looping forever
    assert final_clip["status"] in (js.CLIP_REPAIR_REQUIRED, js.CLIP_PASSED)


def test_episode_marked_incomplete_not_assembled_when_no_video_files_exist(isolated_root):
    """Regression test for a real bug found during manual verification:
    the orchestrator used to mark an episode ASSEMBLED purely from clip QA
    status, without ever actually calling the Episode Assembler -- so it
    would falsely claim ASSEMBLED even with zero real video files on disk.
    Fixed to call assemble_episode() for real and only report ASSEMBLED
    if it actually produced a file."""
    from tools.continuity.clip_output_registrar import register_clip_output
    from tools.providers.veo31_fast import Veo31FastProvider

    register_season_concept(isolated_root, {
        "season_id": "orch8", "theme": "t", "language": "English", "target_age": "5-8",
        "episode_count": 1, "episode_duration_minutes": 5,
        "premises": [{"episode_id": "ep_o1", "title": "t", "premise": "t", "arc_position": "opener"}],
    })
    register_authored_episode(isolated_root, "orch8", SIMPLE_EPISODE)
    state = generate_season(isolated_root, season_id="orch8", theme="t", episode_count=1,
                             episode_duration_minutes=5, language="English", target_age="5-8",
                             author_provider=None, veo_executor=None, _test_only_disable_gates=_SKIP_GATES)
    caps = Veo31FastProvider().capabilities()
    ep = state["episodes"]["ep_o1"]
    for clip_key in ep["clips"]:
        scene_id, clip_id = clip_key.split("/")
        # Register output WITHOUT ever creating a real video file --
        # exactly the gap that exposed the bug.
        register_clip_output(isolated_root, "ep_o1", scene_id, clip_id,
                              provider_capabilities=caps, last_frame_path="continuity/frames/fake.jpg")

    final = generate_season(isolated_root, season_id="orch8", theme="t", episode_count=1,
                             episode_duration_minutes=5, language="English", target_age="5-8",
                             author_provider=None, veo_executor=None, _test_only_disable_gates=_SKIP_GATES)
    assert final["episodes"]["ep_o1"]["status"] == "INCOMPLETE"
    # a real, itemized report must exist explaining exactly why
    report_path = isolated_root / "continuity" / "assembly_reports" / "ep_o1.json"
    assert report_path.exists()
    import json
    report = json.loads(report_path.read_text())
    assert report["assembled"] is False
    assert report["missing_clips"]


def test_generate_season_is_idempotent_on_season_id(isolated_root):
    generate_season(isolated_root, season_id="orch5", theme="t", episode_count=1,
                     episode_duration_minutes=5, language="English", target_age="5-8",
                     author_provider=None, veo_executor=None, _test_only_disable_gates=_SKIP_GATES)
    job1 = JobStateRepo(isolated_root).load("orch5")

    # Calling again with DIFFERENT parameters must not reset the existing job
    generate_season(isolated_root, season_id="orch5", theme="COMPLETELY DIFFERENT",
                     episode_count=99, episode_duration_minutes=99, language="French",
                     target_age="99", author_provider=None, veo_executor=None, _test_only_disable_gates=_SKIP_GATES)
    job2 = JobStateRepo(isolated_root).load("orch5")
    assert job2.theme == "t"
    assert job2.episode_count == 1
