"""
tools/providers/veo31.py — Veo 3.1 provider adapter.

Translates a provider-agnostic ContinuityRequest into the payload shape
documented at ai.google.dev/gemini-api/docs/veo (generateContent /
predictLongRunning). This module is the ONLY place Veo-specific payload
field names should appear.
"""
from __future__ import annotations

from pathlib import Path

from tools.providers.base import (
    ProviderCapabilities,
    ValidationError,
    VideoProvider,
    load_capabilities,
)

CAPABILITY_FILE = (
    Path(__file__).resolve().parents[2] / "continuity" / "providers" / "capabilities" / "veo_3_1.json"
)


class Veo31Provider(VideoProvider):
    def __init__(self, capability_file: str | Path = CAPABILITY_FILE):
        self._capabilities = load_capabilities(capability_file)

    def capabilities(self) -> ProviderCapabilities:
        return self._capabilities

    def validate_request(self, request: dict) -> list[ValidationError]:
        caps = self._capabilities
        errors: list[ValidationError] = []

        ref_images = request.get("reference_images") or []
        if len(ref_images) > caps.max_reference_images:
            errors.append(ValidationError(
                field="reference_images",
                message=(
                    f"{len(ref_images)} reference images given, provider "
                    f"{caps.provider_id} supports at most {caps.max_reference_images}. "
                    "Reference Image Manager should have truncated this before it "
                    "reached the provider."
                ),
            ))

        settings = request.get("generation_settings") or {}
        duration = settings.get("duration_seconds")
        resolution = settings.get("resolution", "720p")
        if resolution not in caps.resolution_options:
            errors.append(ValidationError(
                field="generation_settings.resolution",
                message=f"'{resolution}' not in supported resolutions {caps.resolution_options}",
            ))
        if duration is not None:
            allowed = caps.max_duration_seconds(
                using_reference_images=bool(ref_images),
                resolution=resolution,
                using_extension=bool(request.get("previous_frame_image") and
                                      request.get("continuation_mode") == "video_extension"),
            )
            if bool(ref_images) or resolution in ("1080p", "4k"):
                if duration != 8:
                    errors.append(ValidationError(
                        field="generation_settings.duration_seconds",
                        message=(
                            f"duration must be 8s when using reference images or "
                            f"{resolution} resolution, got {duration}s"
                        ),
                    ))
            elif duration not in caps.duration_options_seconds:
                errors.append(ValidationError(
                    field="generation_settings.duration_seconds",
                    message=f"{duration}s not in {caps.duration_options_seconds}",
                ))

        aspect_ratio = settings.get("aspect_ratio", "16:9")
        if aspect_ratio not in caps.aspect_ratios:
            errors.append(ValidationError(
                field="generation_settings.aspect_ratio",
                message=f"'{aspect_ratio}' not in supported aspect ratios {caps.aspect_ratios}",
            ))

        continuation_mode = request.get("continuation_mode")
        if continuation_mode == "video_extension" and not caps.supports_video_extension:
            errors.append(ValidationError(
                field="continuation_mode",
                message=f"continuation_mode='video_extension' requested but {caps.provider_id} "
                        f"does not support video extension -- invalid payload combination",
            ))
        if continuation_mode == "first_frame" and not caps.supports_image_to_video:
            errors.append(ValidationError(
                field="continuation_mode",
                message=f"continuation_mode='first_frame' requested but {caps.provider_id} "
                        f"does not support image-to-video -- invalid payload combination",
            ))
        if continuation_mode is not None and not request.get("previous_frame_image"):
            errors.append(ValidationError(
                field="previous_frame_image",
                message=f"continuation_mode='{continuation_mode}' set but no previous_frame_image "
                        f"provided -- invalid payload combination",
            ))
        if ref_images and not caps.supports_reference_images:
            errors.append(ValidationError(
                field="reference_images",
                message=f"reference images provided but {caps.provider_id} does not support "
                        f"reference images at all -- invalid payload combination",
            ))

        prompt = request.get("prompt", "")
        # Rough token estimate (~4 chars/token); real tokenization not needed
        # for a pre-flight sanity check, just to catch gross overflows early.
        if len(prompt) / 4 > caps.max_prompt_tokens:
            errors.append(ValidationError(
                field="prompt",
                message=f"prompt looks like it exceeds ~{caps.max_prompt_tokens} tokens",
                severity="warning",
            ))

        return errors

    def build_payload(self, request: dict) -> dict:
        caps = self._capabilities
        settings = request.get("generation_settings") or {}
        ref_images = request.get("reference_images") or []

        payload: dict = {
            "model": caps.model_id,
            "instances": [
                {
                    "prompt": self._compose_prompt(request),
                }
            ],
            "parameters": {
                "aspectRatio": settings.get("aspect_ratio", "16:9"),
                "resolution": settings.get("resolution", "720p"),
                "durationSeconds": str(settings.get(
                    "duration_seconds",
                    caps.max_duration_seconds(using_reference_images=bool(ref_images)),
                )),
                "personGeneration": self._person_generation_mode(request),
            },
        }

        if ref_images:
            payload["instances"][0]["referenceImages"] = [
                {
                    "image": {"path": img["path"]},
                    "referenceType": img.get("reference_type", "asset"),
                }
                for img in ref_images
            ]

        previous_frame = request.get("previous_frame_image")
        continuation_mode = request.get("continuation_mode")
        if previous_frame and continuation_mode == "first_frame":
            payload["instances"][0]["image"] = {"path": previous_frame}
        elif previous_frame and continuation_mode == "video_extension":
            payload["instances"][0]["video"] = {"path": previous_frame}

        last_frame = request.get("last_frame_image")
        if last_frame:
            payload["instances"][0]["lastFrame"] = {"path": last_frame}

        return payload

    @staticmethod
    def _compose_prompt(request: dict) -> str:
        prompt = request.get("prompt", "")
        negatives = request.get("negative_constraints") or []
        if negatives:
            prompt = prompt.rstrip() + "\n\nAvoid: " + "; ".join(negatives) + "."
        return prompt

    @staticmethod
    def _person_generation_mode(request: dict) -> str:
        uses_image_input = bool(
            request.get("reference_images") or request.get("previous_frame_image")
        )
        return "allow_adult" if uses_image_input else "allow_all"
