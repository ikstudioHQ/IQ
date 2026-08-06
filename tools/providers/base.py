"""
tools/providers/base.py — Provider Adapter abstraction layer.

The rest of the Visual Continuity Foundation (Reference Image Manager,
Request Payload Builder, Continuity Assembler) must NEVER read a number
like "3 reference images" or "8 seconds" as a literal. Every such
constraint comes from a ProviderCapabilities object, loaded from a JSON
file under continuity/providers/capabilities/. Adding a new AI video
provider means writing one new capability JSON file and one new
VideoProvider subclass -- nothing else in the codebase changes.

This module has no dependency on any specific provider's SDK. It defines
the contract only.
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProviderCapabilities:
    """Everything downstream code is allowed to know about a provider's
    hard limits. Populated from a JSON capability file, never hand-built
    with hardcoded numbers in Python."""

    provider_id: str
    model_id: str
    max_reference_images: int
    supports_reference_images: bool
    supports_image_to_video: bool
    supports_last_frame_interpolation: bool
    supports_video_extension: bool
    duration_options_seconds: list[int]
    duration_forced_to_8_when: list[str]
    resolution_options: list[str]
    aspect_ratios: list[str]
    frame_rate_fps: int
    max_prompt_tokens: int
    videos_per_request: int
    video_retention_days: int
    person_generation_modes: dict[str, list[str]]
    supports_style_reference_image: bool = False
    extension: dict[str, Any] = field(default_factory=dict)
    region_restrictions: dict[str, str] = field(default_factory=dict)
    notes: str = ""

    @classmethod
    def from_json_file(cls, path: str | Path) -> "ProviderCapabilities":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        known_fields = {f for f in cls.__dataclass_fields__}
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)

    def max_duration_seconds(self, *, using_reference_images: bool = False,
                              resolution: str = "720p",
                              using_extension: bool = False) -> int:
        """Resolve the actual duration ceiling for a specific clip request,
        given the provider's 'forced to 8s when X' rules. Business logic
        calls this instead of assuming any duration is always available."""
        forces_8 = (
            ("reference_images_used" in self.duration_forced_to_8_when and using_reference_images)
            or ("resolution_1080p_or_4k" in self.duration_forced_to_8_when and resolution in ("1080p", "4k"))
            or ("extension_used" in self.duration_forced_to_8_when and using_extension)
        )
        if forces_8:
            return 8
        return max(self.duration_options_seconds)


@dataclass(frozen=True)
class ValidationError:
    field: str
    message: str
    severity: str = "error"  # "error" blocks the request, "warning" does not


class VideoProvider(ABC):
    """Interface every AI video provider adapter implements. Nothing
    outside tools/providers/ should import a provider-specific SDK or
    know a provider-specific payload shape."""

    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        ...

    @abstractmethod
    def validate_request(self, request: dict) -> list[ValidationError]:
        """request is a ContinuityRequest.to_dict() (see
        tools/continuity/request_payload_builder.py). Returns a list of
        problems found BEFORE any payload is built -- e.g. too many
        reference images, unsupported duration, missing required field.
        Empty list = request is valid for this provider."""
        ...

    @abstractmethod
    def build_payload(self, request: dict) -> dict:
        """Converts a provider-agnostic ContinuityRequest dict into the
        exact shape this provider's API expects. Does NOT call any API --
        this phase only builds the payload for inspection/storage."""
        ...


def load_capabilities(capability_file: str | Path) -> ProviderCapabilities:
    return ProviderCapabilities.from_json_file(capability_file)
