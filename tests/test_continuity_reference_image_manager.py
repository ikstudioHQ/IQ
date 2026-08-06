import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.continuity.reference_image_manager import ReferenceImageManager
from tools.providers.base import ProviderCapabilities

FAKE_CAPS_LIMIT_1 = ProviderCapabilities(
    provider_id="fake", model_id="fake", max_reference_images=1,
    supports_reference_images=True, supports_image_to_video=True,
    supports_last_frame_interpolation=True, supports_video_extension=False,
    duration_options_seconds=[8], duration_forced_to_8_when=[],
    resolution_options=["720p"], aspect_ratios=["16:9"], frame_rate_fps=24,
    max_prompt_tokens=1024, videos_per_request=1, video_retention_days=2,
    person_generation_modes={},
)

FAKE_CAPS_LIMIT_5 = ProviderCapabilities(
    provider_id="fake5", model_id="fake5", max_reference_images=5,
    supports_reference_images=True, supports_image_to_video=True,
    supports_last_frame_interpolation=True, supports_video_extension=False,
    duration_options_seconds=[8], duration_forced_to_8_when=[],
    resolution_options=["720p"], aspect_ratios=["16:9"], frame_rate_fps=24,
    max_prompt_tokens=1024, videos_per_request=1, video_retention_days=2,
    person_generation_modes={},
)

FAKE_CAPS_NO_IMAGES = ProviderCapabilities(
    provider_id="fakeno", model_id="fakeno", max_reference_images=0,
    supports_reference_images=False, supports_image_to_video=False,
    supports_last_frame_interpolation=False, supports_video_extension=False,
    duration_options_seconds=[8], duration_forced_to_8_when=[],
    resolution_options=["720p"], aspect_ratios=["16:9"], frame_rate_fps=24,
    max_prompt_tokens=1024, videos_per_request=1, video_retention_days=2,
    person_generation_modes={},
)


def test_get_for_character_zayd_resolves(repo_root):
    mgr = ReferenceImageManager(repo_root)
    assets = mgr.get_for_character("char_001_zayd")
    assert len(assets) == 1
    assert assets[0].resolves_on_disk is True


def test_select_for_clip_respects_limit_of_1(repo_root):
    mgr = ReferenceImageManager(repo_root)
    selected, dropped = mgr.select_for_clip(
        primary_character_ids=["char_001_zayd"],
        secondary_character_ids=["char_002_amira"],
        environment_id="loc_family_living_room",
        prop_ids=["prop_grocery_bag_01"],
        capabilities=FAKE_CAPS_LIMIT_1,
    )
    assert len(selected) == 1
    assert selected[0].owner_id == "char_001_zayd"  # primary wins priority
    assert len(dropped) >= 1


def test_select_for_clip_respects_limit_of_5_not_hardcoded_3(repo_root):
    mgr = ReferenceImageManager(repo_root)
    selected, dropped = mgr.select_for_clip(
        primary_character_ids=["char_001_zayd", "char_002_amira"],
        secondary_character_ids=["char_003_ummi_layla"],
        environment_id=None,
        prop_ids=[],
        capabilities=FAKE_CAPS_LIMIT_5,
    )
    # only 3 candidates exist (2 primary + 1 secondary), all should fit under limit 5
    assert len(selected) == 3
    assert dropped == []


def test_priority_order_primary_before_secondary(repo_root):
    mgr = ReferenceImageManager(repo_root)
    selected, _ = mgr.select_for_clip(
        primary_character_ids=["char_002_amira"],
        secondary_character_ids=["char_001_zayd"],
        environment_id=None,
        prop_ids=[],
        capabilities=FAKE_CAPS_LIMIT_1,
    )
    assert selected[0].owner_id == "char_002_amira"
    assert selected[0].role == "primary_character"


def test_no_reference_image_support_returns_empty(repo_root):
    mgr = ReferenceImageManager(repo_root)
    selected, dropped = mgr.select_for_clip(
        primary_character_ids=["char_001_zayd"],
        secondary_character_ids=[],
        environment_id=None,
        prop_ids=[],
        capabilities=FAKE_CAPS_NO_IMAGES,
    )
    assert selected == []
    assert len(dropped) == 1


def test_unknown_character_returns_no_assets(repo_root):
    mgr = ReferenceImageManager(repo_root)
    assert mgr.get_for_character("char_999_nobody") == []
