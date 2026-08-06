"""
tools/continuity/request_payload_builder.py

Builds a provider-agnostic ContinuityRequest -- prompt, negative
constraints, reference images, previous-frame reference, camera/music
metadata, generation settings -- from a SceneClipSpec plus the
continuity bibles. The prompt is only ONE field of the result, not the
whole output (this is the actual fix for the "text-only prompt
generator" gap identified in Phase 1).

Reuses tools/gemini_shared.py's text-cleaning functions rather than
duplicating them, per the Phase 2 backward-compatibility commitment.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from tools.continuity.clip_state import ClipState
from tools.continuity.clip_output_registrar import video_extension_still_valid
from tools.continuity.camera_bible import CameraBible
from tools.continuity.environment_continuity import EnvironmentContinuityResolver
from tools.continuity.id_validation import validate_registry_ids
from tools.continuity.reference_image_manager import ReferenceImageManager
from tools.continuity.safety_check import SafetyChecker
from tools.gemini_shared import strip_dependencies, strip_scaffold, truncate_at_sentence
from tools.providers.base import ProviderCapabilities


@dataclass
class SceneClipSpec:
    """What the (unmodified) authoring/roadmap layer hands to the
    continuity system for one clip. This is the input contract Phase 2
    depends on from upstream -- authoring itself is not redesigned this
    phase."""
    episode_id: str
    scene_id: str
    clip_id: str
    sequence_index: int
    primary_character_ids: list[str]
    secondary_character_ids: list[str] = field(default_factory=list)
    environment_id: Optional[str] = None
    prop_ids: list[str] = field(default_factory=list)
    camera: dict[str, Any] = field(default_factory=dict)
    lighting: dict[str, Any] = field(default_factory=dict)
    emotions: dict[str, str] = field(default_factory=dict)
    music: dict[str, Any] = field(default_factory=dict)
    raw_prompt_text: str = ""
    negative_constraints: list[str] = field(default_factory=list)
    previous_clip_id: Optional[str] = None
    scene_type: Optional[str] = None  # looked up in Camera Bible to fill camera gaps; explicit `camera` fields always win
    environment_overrides: dict[str, Any] = field(default_factory=dict)  # explicit story-driven changes; else state carries forward -- see EnvironmentContinuityResolver


@dataclass
class ContinuityRequest:
    clip_context: dict[str, str]
    prompt: str
    negative_constraints: list[str]
    reference_images: list[dict]
    previous_frame_image: Optional[str]
    last_frame_image: Optional[str]
    continuation_mode: Optional[str]  # None | "first_frame" | "video_extension"
    camera_metadata: dict[str, Any]
    music_metadata: dict[str, Any]
    generation_settings: dict[str, Any]
    environment_metadata: dict[str, Any] = field(default_factory=dict)
    environment_provenance: dict[str, str] = field(default_factory=dict)
    dropped_reference_notes: list[str] = field(default_factory=list)
    # Phase 4 additions -- always populated, never bolted on after the fact,
    # so a serialized request is self-contained: everything needed to decide
    # whether it's safe/valid to send is already on the object.
    safety_findings: list[dict] = field(default_factory=list)
    diagnostics: list[dict] = field(default_factory=list)  # builder-level notes: missing assets, missing continuation anchor, etc.

    def to_dict(self) -> dict:
        return asdict(self)

    def has_blocking_issues(self) -> bool:
        return any(f["severity"] == "error" for f in self.safety_findings) or \
               any(d["severity"] == "error" for d in self.diagnostics)


class RequestPayloadBuilder:
    def __init__(self, root: str, ref_manager: Optional[ReferenceImageManager] = None):
        self.root = root
        self.ref_manager = ref_manager or ReferenceImageManager(root)
        self.camera_bible = CameraBible(root)
        self.env_resolver = EnvironmentContinuityResolver(root)
        self.safety_checker = SafetyChecker(root)

    def _clean_prompt(self, raw_text: str) -> str:
        text = strip_scaffold(raw_text)
        text = strip_dependencies(text)
        text = truncate_at_sentence(text, max_chars=900)
        return text.strip()

    def build(
        self,
        spec: SceneClipSpec,
        *,
        provider_capabilities: ProviderCapabilities,
        previous_clip_state: Optional[ClipState] = None,
        target_resolution: str = "720p",
        aspect_ratio: str = "16:9",
        forced_reference_owner_ids: Optional[list[str]] = None,
        extra_negative_constraints: Optional[list[str]] = None,
    ) -> ContinuityRequest:
        # Root-cause fix for the Phase 8 BLOCKER: validate every
        # character/environment/prop ID against the canonical registries
        # BEFORE anything else runs. This is the one chokepoint every clip
        # passes through regardless of how the SceneClipSpec was built, so
        # fixing it here (rather than only in the Scene-to-Clip Bridge)
        # guarantees no unknown ID reaches a prompt or payload from any
        # path, present or future. Never removes/substitutes an invalid
        # ID -- fails the whole request closed with a specific diagnostic
        # per bad ID instead.
        id_errors = validate_registry_ids(
            self.root,
            character_ids=spec.primary_character_ids + spec.secondary_character_ids,
            environment_id=spec.environment_id,
            prop_ids=spec.prop_ids,
        )
        if id_errors:
            return ContinuityRequest(
                clip_context={
                    "episode_id": spec.episode_id, "scene_id": spec.scene_id, "clip_id": spec.clip_id,
                },
                # Deliberately NOT spec.raw_prompt_text: that text may
                # already contain a leaked raw ID (e.g. the bridge's own
                # composed dialogue for an unknown character). Never let
                # it reach this object at all, so it can never reach a
                # serialized request, an inspector, or a payload.
                prompt="[BLOCKED -- request not built: references unknown registry ID(s), see diagnostics]",
                negative_constraints=[], reference_images=[], previous_frame_image=None,
                last_frame_image=None, continuation_mode=None, camera_metadata={}, music_metadata={},
                generation_settings={}, environment_metadata={}, environment_provenance={},
                dropped_reference_notes=[], safety_findings=[], diagnostics=id_errors,
            )

        selected_refs, dropped = self.ref_manager.select_for_clip(
            primary_character_ids=spec.primary_character_ids,
            secondary_character_ids=spec.secondary_character_ids,
            environment_id=spec.environment_id,
            prop_ids=spec.prop_ids,
            capabilities=provider_capabilities,
            forced_owner_ids=forced_reference_owner_ids,
        )
        reference_images = [
            {"path": a.path, "role": a.role, "owner_id": a.owner_id, "reference_type": "asset"}
            for a in selected_refs
        ]

        diagnostics: list[dict] = []
        for a in selected_refs:
            for err in self.ref_manager.validate(a):
                diagnostics.append({
                    "source": "reference_image_manager",
                    "field": f"reference_images.{a.owner_id}",
                    "message": err.message,
                    "severity": err.severity,
                })
        # select_for_clip() (Phase 2/3, unchanged) silently excludes any
        # candidate whose image doesn't resolve on disk -- correct for
        # selection purposes, but it means a broken asset would otherwise
        # never surface anywhere. Phase 4's "missing assets" validation
        # requirement needs it visible, so check the full candidate set
        # here (a strict superset of what got selected) independently of
        # the selection filter above.
        for cid in spec.primary_character_ids + spec.secondary_character_ids:
            for a in self.ref_manager.get_for_character(cid):
                if not a.resolves_on_disk:
                    diagnostics.append({
                        "source": "reference_image_manager",
                        "field": f"reference_images.{cid}",
                        "message": f"reference image for {cid} does not resolve on disk: {a.path}",
                        "severity": "warning",
                    })
        for pid in spec.prop_ids:
            for a in self.ref_manager.get_for_prop(pid):
                if not a.resolves_on_disk:
                    diagnostics.append({
                        "source": "reference_image_manager",
                        "field": f"reference_images.{pid}",
                        "message": f"reference image for {pid} does not resolve on disk: {a.path}",
                        "severity": "warning",
                    })
        if spec.environment_id:
            for a in self.ref_manager.get_for_environment(spec.environment_id):
                if not a.resolves_on_disk:
                    diagnostics.append({
                        "source": "reference_image_manager",
                        "field": f"reference_images.{spec.environment_id}",
                        "message": f"reference image for {spec.environment_id} does not resolve on disk: {a.path}",
                        "severity": "warning",
                    })

        previous_frame_image = None
        continuation_mode = None
        if previous_clip_state is not None:
            prev_output = previous_clip_state.output or {}
            if (
                provider_capabilities.supports_video_extension
                and video_extension_still_valid(prev_output)
            ):
                previous_frame_image = prev_output.get("video_reference")
                continuation_mode = "video_extension"
            elif provider_capabilities.supports_image_to_video and prev_output.get("last_frame_path"):
                previous_frame_image = prev_output.get("last_frame_path")
                continuation_mode = "first_frame"
            # else: previous clip hasn't been generated yet (output empty) or
            # its video expired with no last-frame image saved -- fall back
            # to text-only continuity for this clip rather than erroring.

        if spec.previous_clip_id and continuation_mode is None:
            diagnostics.append({
                "source": "request_payload_builder",
                "field": "continuation_mode",
                "message": (
                    f"clip declares previous_clip_id='{spec.previous_clip_id}' but no continuation "
                    f"anchor was found (previous clip not yet generated, or its output expired with "
                    f"no last-frame saved). This clip will generate with text-only continuity to its "
                    f"predecessor -- visual drift risk."
                ),
                "severity": "warning",
            })

        duration = provider_capabilities.max_duration_seconds(
            using_reference_images=bool(reference_images),
            resolution=target_resolution,
            using_extension=(continuation_mode == "video_extension"),
        )

        prompt = self._clean_prompt(spec.raw_prompt_text)
        camera_metadata = self.camera_bible.resolve_camera_metadata(spec.scene_type, spec.camera)

        env_overrides = {**spec.lighting, **spec.environment_overrides}
        resolved_environment, env_provenance = self.env_resolver.resolve(
            spec.environment_id, env_overrides, exclude_clip_id=spec.clip_id,
        )
        negative_constraints = list(spec.negative_constraints)
        continuity_note = self.env_resolver.continuity_note_for_prompt(spec.environment_id)
        if continuity_note:
            negative_constraints.append(f"maintain environment continuity: {continuity_note}")
        if extra_negative_constraints:
            negative_constraints.extend(extra_negative_constraints)

        safety_findings = [
            {
                "source": f.source, "rule_id": f.rule_id, "category": f.category,
                "level": f.level, "matched_text": f.matched_text,
                "message": f.message, "severity": f.severity,
            }
            for f in self.safety_checker.scan(prompt)
        ]

        request = ContinuityRequest(
            clip_context={
                "episode_id": spec.episode_id,
                "scene_id": spec.scene_id,
                "clip_id": spec.clip_id,
            },
            prompt=prompt,
            negative_constraints=negative_constraints,
            reference_images=reference_images,
            previous_frame_image=previous_frame_image,
            last_frame_image=None,  # populated only when authoring plans a deliberate end-state (interpolation mode); not used by the default carry-forward path
            continuation_mode=continuation_mode,
            camera_metadata=camera_metadata,
            music_metadata=spec.music,
            generation_settings={
                "duration_seconds": duration,
                "resolution": target_resolution,
                "aspect_ratio": aspect_ratio,
            },
            environment_metadata=resolved_environment,
            environment_provenance=env_provenance,
            dropped_reference_notes=dropped,
            safety_findings=safety_findings,
            diagnostics=diagnostics,
        )
        return request
