import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.providers.veo31 import Veo31Provider
from tools.providers.veo31_fast import Veo31FastProvider
from tools.providers.registry import get_provider, available_providers


def test_capabilities_load_from_json():
    p = Veo31Provider()
    caps = p.capabilities()
    assert caps.max_reference_images == 3
    assert caps.supports_reference_images is True
    assert 8 in caps.duration_options_seconds


def test_duration_forced_to_8_with_reference_images():
    caps = Veo31Provider().capabilities()
    assert caps.max_duration_seconds(using_reference_images=True) == 8
    assert caps.max_duration_seconds(using_reference_images=False) in caps.duration_options_seconds


def test_duration_forced_to_8_at_1080p():
    caps = Veo31Provider().capabilities()
    assert caps.max_duration_seconds(resolution="1080p") == 8
    assert caps.max_duration_seconds(resolution="720p") != 8 or 8 == max(caps.duration_options_seconds)


def test_validate_request_rejects_too_many_reference_images():
    p = Veo31Provider()
    caps = p.capabilities()
    request = {
        "reference_images": [{"path": f"x{i}.png"} for i in range(caps.max_reference_images + 1)],
        "generation_settings": {"duration_seconds": 8, "resolution": "720p", "aspect_ratio": "16:9"},
        "prompt": "test",
    }
    errors = p.validate_request(request)
    assert any(e.field == "reference_images" for e in errors)


def test_validate_request_accepts_within_limit():
    p = Veo31Provider()
    caps = p.capabilities()
    request = {
        "reference_images": [{"path": "x.png"}] * caps.max_reference_images,
        "generation_settings": {"duration_seconds": 8, "resolution": "720p", "aspect_ratio": "16:9"},
        "prompt": "test",
    }
    errors = p.validate_request(request)
    assert not any(e.severity == "error" for e in errors)


def test_build_payload_includes_reference_images():
    p = Veo31Provider()
    request = {
        "prompt": "A cat enters a room.",
        "negative_constraints": ["no duplicate cats"],
        "reference_images": [{"path": "assets/cat.png", "reference_type": "asset"}],
        "generation_settings": {"duration_seconds": 8, "resolution": "720p", "aspect_ratio": "16:9"},
    }
    payload = p.build_payload(request)
    assert payload["model"] == "veo-3.1-generate-preview"
    assert "referenceImages" in payload["instances"][0]
    assert "Avoid: no duplicate cats" in payload["instances"][0]["prompt"]


def test_fast_provider_uses_fast_model_id():
    p = Veo31FastProvider()
    assert p.capabilities().model_id == "veo-3.1-fast-generate-preview"
    assert p.capabilities().max_reference_images == 3


def test_registry_lookup():
    assert set(available_providers()) == {"veo-3.1", "veo-3.1-fast"}
    assert get_provider("veo-3.1").capabilities().provider_id == "veo-3.1"
    try:
        get_provider("nonexistent")
        assert False, "should have raised"
    except ValueError:
        pass
