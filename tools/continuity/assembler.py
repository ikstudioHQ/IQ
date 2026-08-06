"""
tools/continuity/assembler.py

ContinuityAssembler is the single entry point Phase 3+ (and eventually
the orchestrator) calls per clip. It ties together the Character/
Environment/Prop bibles, Clip State DB, Reference Image Manager,
Request Payload Builder, and Provider Adapter -- and writes the
resulting ClipState back with qa_status="PENDING" (Phase 5 fills in
real QA later; this phase never marks anything APPROVED).

Does NOT call any external API. Returns the provider-agnostic request
and the provider-specific payload for inspection/storage.
"""
from __future__ import annotations

from typing import Optional

from tools.continuity.clip_state import ClipState, ClipStateRepo
from tools.continuity.reference_image_manager import ReferenceImageManager
from tools.continuity.request_payload_builder import (
    ContinuityRequest,
    RequestPayloadBuilder,
    SceneClipSpec,
)
from tools.continuity.request_serializer import serialize_request
from tools.providers.base import VideoProvider, ValidationError


class ContinuityAssembler:
    def __init__(self, root: str, provider: VideoProvider):
        self.root = root
        self.provider = provider
        self.ref_manager = ReferenceImageManager(root)
        self.payload_builder = RequestPayloadBuilder(root, self.ref_manager)
        self.clip_state_repo = ClipStateRepo(root)

    def process_clip(
        self,
        spec: SceneClipSpec,
        *,
        target_resolution: str = "720p",
        aspect_ratio: str = "16:9",
        forced_reference_owner_ids: Optional[list[str]] = None,
        extra_negative_constraints: Optional[list[str]] = None,
    ) -> tuple[ContinuityRequest, dict, list[ValidationError]]:
        previous_state = None
        if spec.previous_clip_id:
            previous_state = self.clip_state_repo.load(
                spec.episode_id, spec.scene_id, spec.previous_clip_id
            )

        request = self.payload_builder.build(
            spec,
            provider_capabilities=self.provider.capabilities(),
            previous_clip_state=previous_state,
            target_resolution=target_resolution,
            aspect_ratio=aspect_ratio,
            forced_reference_owner_ids=forced_reference_owner_ids,
            extra_negative_constraints=extra_negative_constraints,
        )

        request_dict = request.to_dict()
        # Fail fast on safety errors / builder diagnostics BEFORE even asking
        # the provider to validate -- a NEVER_GENERATE safety hit shouldn't
        # reach provider-specific validation at all, per Phase 4's safety
        # integration requirement.
        errors = self.provider.validate_request(request_dict) if not request.has_blocking_issues() else []
        payload = {}
        if not request.has_blocking_issues() and not any(e.severity == "error" for e in errors):
            payload = self.provider.build_payload(request_dict)

        blocked = request.has_blocking_issues() or any(e.severity == "error" for e in errors)

        serialize_request(
            self.root, request, payload, errors,
            provider_id=self.provider.capabilities().provider_id,
        )

        clip_state = ClipState(
            episode_id=spec.episode_id,
            scene_id=spec.scene_id,
            clip_id=spec.clip_id,
            sequence_index=spec.sequence_index,
            continuity_thread_id=f"{spec.episode_id}__{spec.scene_id}",
            previous_clip_id=spec.previous_clip_id,
            characters_present=spec.primary_character_ids + spec.secondary_character_ids,
            environment={"location_id": spec.environment_id, **request.environment_metadata} if spec.environment_id else {},
            camera=request.camera_metadata,
            lighting=request.environment_metadata,
            props_visible=spec.prop_ids,
            emotions=spec.emotions,
            music=spec.music,
            prompt_text=request.prompt,
            reference_images_used=request.reference_images,
            previous_frame_used=request.previous_frame_image,
            provider=self.provider.capabilities().model_id,
            generation_settings=request.generation_settings,
            qa_status="BLOCKED" if blocked else "PENDING",
        )
        self.clip_state_repo.save(clip_state)

        return request, payload, errors
