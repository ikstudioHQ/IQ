"""
tools/providers/registry.py — lookup table from provider_id to
VideoProvider implementation. Adding a new provider means adding one
line here plus its own module -- nothing else in the codebase changes.
"""
from __future__ import annotations

from tools.providers.base import VideoProvider
from tools.providers.veo31 import Veo31Provider
from tools.providers.veo31_fast import Veo31FastProvider

_REGISTRY: dict[str, type[VideoProvider]] = {
    "veo-3.1": Veo31Provider,
    "veo-3.1-fast": Veo31FastProvider,
}


def get_provider(provider_id: str) -> VideoProvider:
    try:
        cls = _REGISTRY[provider_id]
    except KeyError as exc:
        raise ValueError(
            f"Unknown provider_id '{provider_id}'. Known providers: {sorted(_REGISTRY)}"
        ) from exc
    return cls()


def available_providers() -> list[str]:
    return sorted(_REGISTRY)
