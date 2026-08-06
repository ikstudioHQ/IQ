import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def repo_root():
    """Real repo root, read-only usage only (character/environment/prop
    bibles, reference image assets). Do NOT write clip_state or any other
    output under this fixture -- use `isolated_root` for anything that
    writes, so tests never pollute the actual repository with test
    artifacts (continuity/clip_state/ep_test_001/... was exactly this bug
    during Phase 2 development)."""
    return REPO_ROOT


@pytest.fixture
def isolated_root(tmp_path, repo_root):
    """A tmp_path that reads the real bibles/assets via symlink (so no
    large files are copied) but writes clip_state into an isolated,
    auto-cleaned directory. Use this in any test that calls
    ContinuityAssembler.process_clip() or ClipStateRepo.save()."""
    for name in ("sources", "assets", "phase2"):
        src = repo_root / name
        if src.exists():
            os.symlink(src, tmp_path / name, target_is_directory=True)
    # continuity/ is NOT symlinked as a whole -- clip_state must be a real,
    # writable, isolated directory so test writes never touch the repo.
    # Only the read-only bible/provider subdirs are symlinked individually.
    (tmp_path / "continuity").mkdir(parents=True, exist_ok=True)
    for name in ("character_bible", "environment_bible", "prop_registry", "providers"):
        src = repo_root / "continuity" / name
        if src.exists():
            os.symlink(src, tmp_path / "continuity" / name, target_is_directory=True)
    (tmp_path / "continuity" / "clip_state").mkdir(parents=True, exist_ok=True)
    return tmp_path
