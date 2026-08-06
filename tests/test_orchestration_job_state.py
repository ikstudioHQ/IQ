import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.orchestration.job_state import JobStateRepo, SEASON_PENDING_CONCEPT


def test_create_new_job(isolated_root):
    repo = JobStateRepo(isolated_root)
    job = repo.create(season_id="s1", theme="t", episode_count=2, episode_duration_minutes=5,
                       language="English", target_age="5-8", provider_id="veo-3.1-fast")
    assert job.status == SEASON_PENDING_CONCEPT
    assert repo.exists("s1")


def test_create_is_idempotent_returns_existing(isolated_root):
    repo = JobStateRepo(isolated_root)
    job1 = repo.create(season_id="s2", theme="t", episode_count=2, episode_duration_minutes=5,
                        language="English", target_age="5-8", provider_id="veo-3.1-fast")
    job1.status = "IN_PROGRESS"
    repo.save(job1)

    job2 = repo.create(season_id="s2", theme="DIFFERENT THEME", episode_count=99,
                        episode_duration_minutes=99, language="French", target_age="99",
                        provider_id="veo-3.1-fast")
    assert job2.status == "IN_PROGRESS"  # not reset
    assert job2.theme == "t"  # original values preserved, not overwritten


def test_ensure_clip_creates_and_reuses(isolated_root):
    repo = JobStateRepo(isolated_root)
    job = repo.create(season_id="s3", theme="t", episode_count=1, episode_duration_minutes=5,
                       language="English", target_age="5-8", provider_id="veo-3.1-fast")
    c1 = job.ensure_clip("ep01", "scene_01", "clip_01")
    c2 = job.ensure_clip("ep01", "scene_01", "clip_01")
    assert c1 is c2  # same dict object, not recreated
    assert len(job.all_clips()) == 1


def test_save_and_load_round_trip(isolated_root):
    repo = JobStateRepo(isolated_root)
    job = repo.create(season_id="s4", theme="t", episode_count=1, episode_duration_minutes=5,
                       language="English", target_age="5-8", provider_id="veo-3.1-fast")
    job.ensure_clip("ep01", "scene_01", "clip_01")
    repo.save(job)

    loaded = repo.load("s4")
    assert loaded is not None
    assert len(loaded.all_clips()) == 1


def test_load_missing_returns_none(isolated_root):
    repo = JobStateRepo(isolated_root)
    assert repo.load("no_such_season") is None
