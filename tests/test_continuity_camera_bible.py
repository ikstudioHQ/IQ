import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.continuity.camera_bible import CameraBible


def test_known_scene_types_loaded_from_real_data(repo_root):
    cb = CameraBible(repo_root)
    types = cb.known_scene_types()
    assert "curiosity_hook_opening" in types
    assert "intimate_emotional_moment" in types
    assert len(types) == 6


def test_resolve_camera_metadata_fills_gaps_from_bible(repo_root):
    cb = CameraBible(repo_root)
    resolved = cb.resolve_camera_metadata("intimate_emotional_moment", {})
    assert resolved["shot"] is not None
    assert "close-up" in resolved["shot"]


def test_explicit_camera_field_always_wins(repo_root):
    cb = CameraBible(repo_root)
    resolved = cb.resolve_camera_metadata(
        "intimate_emotional_moment", {"shot": "author-specified extreme wide shot"}
    )
    assert resolved["shot"] == "author-specified extreme wide shot"


def test_no_scene_type_returns_explicit_camera_unchanged(repo_root):
    cb = CameraBible(repo_root)
    explicit = {"shot": "medium", "custom_field": "value"}
    resolved = cb.resolve_camera_metadata(None, explicit)
    assert resolved == explicit


def test_unknown_scene_type_falls_back_to_explicit_only(repo_root):
    cb = CameraBible(repo_root)
    resolved = cb.resolve_camera_metadata("not_a_real_scene_type", {"shot": "wide"})
    assert resolved["shot"] == "wide"
