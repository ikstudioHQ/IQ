"""
tools/orchestration/season_orchestrator.py

The actual "click Generate Season" entry point identified as missing in
the Phase 5 gap analysis. advance() is a single, idempotent, resumable
step: call it once, it does whatever work is currently unblocked and
persists everything to disk via JobStateRepo, then returns. Call it
again (same process or a fresh one after a restart) and it continues
from exactly where the persisted state says it left off -- there is no
in-memory-only state anywhere in this pipeline.

Does NOT rebuild any Phase 1-6 component. Every step here is a call
into existing, unmodified functions: ClaudeAuthorProvider/manual seam
(Phase 6), build_clip_specs (Phase 6), ContinuityAssembler.process_clip
(Phase 2-5), run_structural_qa/apply_auto_repair (Phase 5),
VeoExecutor/extract_last_frame (this phase), register_clip_output
(Phase 3).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from tools.authoring.author_provider import AuthorProvider
from tools.authoring.claude_author_provider import MissingCredentialError
from tools.authoring.manual_author_seam import (
    load_authored_episode,
    load_season_concept,
    register_authored_episode,
    register_season_concept,
    write_episode_author_request,
    write_season_concept_request,
)
from tools.authoring.scene_to_clip_bridge import build_clip_specs
from tools.authoring.schemas import EpisodeScript
from tools.continuity.assembler import ContinuityAssembler
from tools.continuity.clip_output_registrar import register_clip_output
from tools.continuity.clip_state import ClipStateRepo
from tools.continuity.qa_engine import run_structural_qa
from tools.continuity.auto_repair import apply_auto_repair, MAX_REPAIR_ATTEMPTS
import json as _json
from tools.orchestration import job_state as js
from tools.orchestration.testing_overrides import DisableProductionGatesForTesting
from tools.orchestration.job_state import JobStateRepo
from tools.orchestration.veo_executor import (
    MissingVeoCredentialError,
    VeoExecutionError,
    VeoExecutor,
    extract_last_frame,
    save_video_from_operation,
)
from tools.providers.registry import get_provider

MAX_CLIP_RETRIES = 3


def _clip_plan_path(root: Path, episode_id: str) -> Path:
    return root / "continuity" / "clip_plan" / f"{episode_id}.json"


def _load_clip_plan(root: Path, episode_id: str) -> Optional[dict]:
    path = _clip_plan_path(root, episode_id)
    if not path.exists():
        return None
    return _json.loads(path.read_text(encoding="utf-8"))


def _save_clip_plan(root: Path, episode_id: str, specs, diagnostics) -> None:
    path = _clip_plan_path(root, episode_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json.dumps({
        "episode_id": episode_id,
        "clips": [s.__dict__ for s in specs],
        "diagnostics": diagnostics,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _local_video_path(root: Path, episode_id: str, scene_id: str, clip_id: str) -> Path:
    return root / "continuity" / "generated_videos" / episode_id / scene_id / f"{clip_id}.mp4"


def _advance_clip(root: Path, provider, veo_executor: Optional[VeoExecutor],
                   auto_execute: bool, episode_id: str, scene_id: str, clip_id: str,
                   spec_by_key: dict, clip_job: dict) -> None:
    key = f"{scene_id}/{clip_id}"

    if clip_job["status"] == js.CLIP_WAITING_FOR_EXTERNAL_GENERATION:
        # Symmetric to the authoring resume path: a human (or later
        # automation) may have generated this clip externally and called
        # register_clip_output() via the manual seam since the last
        # advance(). Check real persisted ClipState, not a flag we'd have
        # to remember to set elsewhere -- if output is populated, resume.
        clip_state = ClipStateRepo(root).load(episode_id, scene_id, clip_id)
        if clip_state and clip_state.output and (
            clip_state.output.get("last_frame_path") or clip_state.output.get("video_reference")
        ):
            clip_job["status"] = js.CLIP_GENERATED
        else:
            return  # genuinely still waiting

    if clip_job["status"] == js.CLIP_PENDING:
        spec = spec_by_key[key]
        assembler = ContinuityAssembler(str(root), provider)
        req, payload, errors = assembler.process_clip(spec)
        if req.has_blocking_issues() or any(e.severity == "error" for e in errors):
            clip_job["status"] = js.CLIP_BLOCKED
            clip_job["last_error"] = "; ".join(
                [f["message"] for f in req.safety_findings if f["severity"] == "error"]
                + [d["message"] for d in req.diagnostics if d["severity"] == "error"]
                + [e.message for e in errors if e.severity == "error"]
            )
            return
        clip_job["status"] = js.CLIP_REQUEST_BUILT

    if clip_job["status"] == js.CLIP_REQUEST_BUILT:
        if not auto_execute or veo_executor is None or not veo_executor.api_key:
            clip_job["status"] = js.CLIP_WAITING_FOR_EXTERNAL_GENERATION
            return
        from tools.continuity.request_serializer import load_serialized_request
        bundle = load_serialized_request(root, episode_id, scene_id, clip_id)
        try:
            operation = veo_executor.generate(provider.capabilities().model_id, bundle["provider_payload"])
            video_path = _local_video_path(root, episode_id, scene_id, clip_id)
            save_video_from_operation(operation, str(video_path))
            frame_path = root / "continuity" / "frames" / episode_id / scene_id / f"{clip_id}_last_frame.jpg"
            extract_last_frame(str(video_path), str(frame_path))
            video_ref = (
                operation.get("response", {}).get("generateVideoResponse", {})
                .get("generatedSamples", [{}])[0].get("video", {}).get("uri")
            )
            register_clip_output(
                root, episode_id, scene_id, clip_id,
                provider_capabilities=provider.capabilities(),
                video_reference=video_ref, last_frame_path=str(frame_path),
            )
            clip_job["status"] = js.CLIP_GENERATED
        except MissingVeoCredentialError:
            clip_job["status"] = js.CLIP_WAITING_FOR_EXTERNAL_GENERATION
        except VeoExecutionError as e:
            clip_job["attempts"] += 1
            clip_job["last_error"] = str(e)
            clip_job["status"] = js.CLIP_FAILED if clip_job["attempts"] >= MAX_CLIP_RETRIES else js.CLIP_REQUEST_BUILT
        return

    if clip_job["status"] == js.CLIP_GENERATED:
        report = run_structural_qa(root, episode_id, scene_id, clip_id)
        if report.overall_status == "PASS":
            clip_job["status"] = js.CLIP_PASSED
        elif report.overall_status == "NEEDS_REPAIR":
            clip_state = ClipStateRepo(root).load(episode_id, scene_id, clip_id)
            if clip_state.repair_attempt < MAX_REPAIR_ATTEMPTS:
                spec = spec_by_key[key]
                apply_auto_repair(root, ContinuityAssembler(str(root), provider), spec)
                clip_job["status"] = js.CLIP_REQUEST_BUILT  # repaired request needs (re)generation
            else:
                clip_job["status"] = js.CLIP_REPAIR_REQUIRED
        else:  # NEEDS_HUMAN_REVIEW or BLOCKED_ON_DEPENDENCY
            clip_job["status"] = js.CLIP_QA_REQUIRED
        return

    if clip_job["status"] == js.CLIP_FAILED and clip_job["attempts"] < MAX_CLIP_RETRIES:
        clip_job["status"] = js.CLIP_REQUEST_BUILT  # allow another attempt next advance()


def advance(root: str | Path, season_id: str, *,
            author_provider: Optional[AuthorProvider] = None,
            veo_executor: Optional[VeoExecutor] = None,
            auto_execute: bool = True,
            _test_only_disable_gates: Optional[DisableProductionGatesForTesting] = None) -> dict:
    """Production gates (Duration, Islamic, Continuity) run automatically
    and unconditionally, by default, on every call. There is no flag to
    turn them off for real production use -- the only way to skip them
    is to explicitly construct and pass a DisableProductionGatesForTesting
    instance from tools.orchestration.testing_overrides, which exists
    specifically and only for tests. Production callers must never pass
    this parameter."""
    root = Path(root)
    repo = JobStateRepo(root)
    job = repo.load(season_id)
    if job is None:
        raise ValueError(f"No job state for season_id={season_id}. Call generate_season() first.")

    # -- Season concept -----------------------------------------------
    if job.status in (js.SEASON_PENDING_CONCEPT, js.SEASON_WAITING_FOR_EXTERNAL_AUTHORING):
        concept = load_season_concept(root, season_id)
        if concept is None:
            if author_provider is not None:
                from tools.authoring.author_provider import build_season_concept_prompt
                prompt = build_season_concept_prompt(
                    theme=job.theme, episode_count=job.episode_count,
                    episode_duration_minutes=job.episode_duration_minutes,
                    language=job.language, target_age=job.target_age,
                )
                try:
                    concept_obj = author_provider.author_season_concept(prompt)
                    register_season_concept(root, concept_obj.to_dict())
                    concept = concept_obj
                except MissingCredentialError:
                    write_season_concept_request(
                        root, season_id=season_id, theme=job.theme, episode_count=job.episode_count,
                        episode_duration_minutes=job.episode_duration_minutes,
                        language=job.language, target_age=job.target_age,
                    )
                    job.status = js.SEASON_WAITING_FOR_EXTERNAL_AUTHORING
                    repo.save(job)
                    return job.to_dict()
            else:
                write_season_concept_request(
                    root, season_id=season_id, theme=job.theme, episode_count=job.episode_count,
                    episode_duration_minutes=job.episode_duration_minutes,
                    language=job.language, target_age=job.target_age,
                )
                job.status = js.SEASON_WAITING_FOR_EXTERNAL_AUTHORING
                repo.save(job)
                return job.to_dict()
        for premise in concept.premises:
            job.ensure_episode(premise["episode_id"])
        job.status = js.SEASON_IN_PROGRESS

    provider = get_provider(job.provider_id)
    concept = load_season_concept(root, season_id)
    premise_by_id = {p["episode_id"]: p for p in (concept.premises if concept else [])}

    for episode_id, ep_job in job.episodes.items():
        if ep_job["status"] == js.EPISODE_PENDING_AUTHORING:
            episode = load_authored_episode(root, episode_id)
            if episode is None:
                premise = premise_by_id.get(episode_id, {})
                if author_provider is not None:
                    from tools.authoring.author_provider import build_episode_prompt
                    prompt = build_episode_prompt(
                        root, episode_id=episode_id, season_id=season_id, theme=job.theme,
                        language=job.language, target_age=job.target_age,
                        premise=premise.get("premise", job.theme),
                        cast_character_ids=[], location_id=None,
                        episode_duration_minutes=job.episode_duration_minutes,
                    )
                    try:
                        script = author_provider.author_episode(prompt)
                        register_authored_episode(root, season_id, script.to_dict())
                        episode = script
                    except MissingCredentialError:
                        write_episode_author_request(
                            root, episode_id=episode_id, season_id=season_id, theme=job.theme,
                            language=job.language, target_age=job.target_age,
                            premise=premise.get("premise", job.theme), cast_character_ids=[],
                            location_id=None, episode_duration_minutes=job.episode_duration_minutes,
                        )
                        ep_job["status"] = js.EPISODE_WAITING_FOR_EXTERNAL_AUTHORING
                        continue
                else:
                    write_episode_author_request(
                        root, episode_id=episode_id, season_id=season_id, theme=job.theme,
                        language=job.language, target_age=job.target_age,
                        premise=premise.get("premise", job.theme), cast_character_ids=[],
                        location_id=None, episode_duration_minutes=job.episode_duration_minutes,
                    )
                    ep_job["status"] = js.EPISODE_WAITING_FOR_EXTERNAL_AUTHORING
                    continue
            ep_job["status"] = js.EPISODE_AUTHORED

        if ep_job["status"] == js.EPISODE_WAITING_FOR_EXTERNAL_AUTHORING:
            episode = load_authored_episode(root, episode_id)
            if episode is None:
                continue  # still waiting, move to next episode
            ep_job["status"] = js.EPISODE_AUTHORED

        if ep_job["status"] == js.EPISODE_AUTHORED:
            episode = load_authored_episode(root, episode_id)

            if _test_only_disable_gates is None:
                from tools.production_gates.duration_gate import duration_gate_check
                from tools.production_gates.islamic_gate import post_authoring_islamic_check
                from tools.production_gates.song_gate import song_gate_check
                islamic = post_authoring_islamic_check(root, episode)
                duration = duration_gate_check(root, episode, provider.capabilities(), job.episode_duration_minutes)
                song = song_gate_check(root, episode)
                if islamic["status"] == "BLOCKED" or duration["status"] in ("TOO_SHORT", "TOO_LONG") or song["status"] == "BLOCKED":
                    ep_job["status"] = js.EPISODE_GATE_REPAIR_REQUIRED
                    ep_job["gate_failure"] = {"islamic": islamic["status"], "duration": duration["status"], "song": song["status"]}
                    continue  # do not proceed to clip planning; move to next episode

            plan = _load_clip_plan(root, episode_id)
            if plan is None:
                specs, diagnostics = build_clip_specs(root, episode, provider.capabilities())
                _save_clip_plan(root, episode_id, specs, diagnostics)
                for spec in specs:
                    job.ensure_clip(episode_id, spec.scene_id, spec.clip_id)
            ep_job["status"] = js.EPISODE_CLIPS_PLANNED

        if ep_job["status"] in (js.EPISODE_CLIPS_PLANNED, js.EPISODE_IN_PROGRESS):
            ep_job["status"] = js.EPISODE_IN_PROGRESS
            plan = _load_clip_plan(root, episode_id)
            spec_by_key = {f"{c['scene_id']}/{c['clip_id']}": _spec_from_dict(c) for c in plan["clips"]}
            for clip_job in ep_job["clips"].values():
                if clip_job["status"] in (js.CLIP_PASSED, js.CLIP_BLOCKED, js.CLIP_REPAIR_REQUIRED, js.CLIP_QA_REQUIRED):
                    continue
                _advance_clip(root, provider, veo_executor, auto_execute,
                               episode_id, clip_job["scene_id"], clip_job["clip_id"],
                               spec_by_key, clip_job)

            statuses = {c["status"] for c in ep_job["clips"].values()}
            settled = {js.CLIP_PASSED, js.CLIP_BLOCKED, js.CLIP_REPAIR_REQUIRED,
                       js.CLIP_QA_REQUIRED, js.CLIP_WAITING_FOR_EXTERNAL_GENERATION, js.CLIP_FAILED}
            if statuses <= settled:
                if statuses == {js.CLIP_PASSED}:
                    from tools.orchestration.episode_assembler import assemble_episode
                    assembly_report = assemble_episode(root, episode_id, ep_job)
                    ep_job["status"] = js.EPISODE_ASSEMBLED if assembly_report["assembled"] else js.EPISODE_INCOMPLETE
                elif statuses & {js.CLIP_WAITING_FOR_EXTERNAL_GENERATION}:
                    pass  # still IN_PROGRESS, waiting on external generation
                else:
                    ep_job["status"] = js.EPISODE_INCOMPLETE

    ep_statuses = {e["status"] for e in job.episodes.values()}
    if ep_statuses and ep_statuses <= {js.EPISODE_ASSEMBLED, js.EPISODE_INCOMPLETE}:
        would_be_complete = ep_statuses == {js.EPISODE_ASSEMBLED}
        if would_be_complete and _test_only_disable_gates is None and job.episodes:
            # Season Acceptance Gate is the final checkpoint: a season is
            # never marked COMPLETE on clip/assembly status alone. This
            # aggregates Duration + Islamic (already checked per-episode
            # above) plus the season-wide Continuity Gate (thread
            # ordering, cross-episode registry validity) that can only be
            # evaluated once every episode's content is known.
            from tools.production_gates.season_acceptance import run_season_acceptance_gate
            acceptance = run_season_acceptance_gate(
                root, season_id, list(job.episodes.keys()), job.provider_id, job.episode_duration_minutes,
            )
            job.season_acceptance = acceptance["status"]
            would_be_complete = acceptance["status"] == "READY"
        job.status = js.SEASON_COMPLETE if would_be_complete else js.SEASON_INCOMPLETE
    elif job.status != js.SEASON_WAITING_FOR_EXTERNAL_AUTHORING:
        job.status = js.SEASON_IN_PROGRESS

    repo.save(job)
    return job.to_dict()


def _spec_from_dict(d: dict):
    from tools.continuity.request_payload_builder import SceneClipSpec
    known = {f for f in SceneClipSpec.__dataclass_fields__}
    return SceneClipSpec(**{k: v for k, v in d.items() if k in known})


def generate_season(root: str | Path, *, season_id: str, theme: str, episode_count: int,
                     episode_duration_minutes: int, language: str, target_age: str,
                     provider_id: str = "veo-3.1-fast",
                     author_provider: Optional[AuthorProvider] = None,
                     veo_executor: Optional[VeoExecutor] = None,
                     auto_execute: bool = True, max_iterations: int = 50,
                     _test_only_disable_gates: Optional[DisableProductionGatesForTesting] = None) -> dict:
    """The one-click entry point. Production gates (Duration, Islamic,
    Continuity, Season Acceptance) run automatically on every call --
    there is no flag for production callers to set or forget. The only
    way to skip them is the explicit, test-only
    DisableProductionGatesForTesting override; production code must
    never construct or pass one.

    Idempotent on season_id -- calling this again after an interruption
    resumes rather than restarts (JobStateRepo.create() returns the
    existing job unchanged if one is already there)."""
    root = Path(root)
    repo = JobStateRepo(root)
    repo.create(
        season_id=season_id, theme=theme, episode_count=episode_count,
        episode_duration_minutes=episode_duration_minutes, language=language,
        target_age=target_age, provider_id=provider_id,
    )

    last_snapshot = None
    for _ in range(max_iterations):
        state = advance(root, season_id, author_provider=author_provider,
                         veo_executor=veo_executor, auto_execute=auto_execute,
                         _test_only_disable_gates=_test_only_disable_gates)
        snapshot = _json.dumps(state, sort_keys=True)
        if state["status"] in (js.SEASON_COMPLETE, js.SEASON_INCOMPLETE, js.SEASON_WAITING_FOR_EXTERNAL_AUTHORING):
            break
        if snapshot == last_snapshot:
            break  # no progress possible right now (e.g. everything waiting on external generation)
        last_snapshot = snapshot
    return state
