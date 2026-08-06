"""
tools/authoring/manual_author_seam.py

The practical path that works today without an API key: writes the
exact same prompt ClaudeAuthorProvider would send (see
author_provider.build_episode_prompt) to a file, for a human -- or this
assistant, in a separate turn with tool access, or any other model --
to run externally and produce a real EpisodeScript/SeasonConcept, then
ingests the result back into the pipeline.

Same shape as register_clip_output() and register_visual_qa_result()
from earlier phases: a deliberate, visible manual step rather than
automation pretending to be automated. Whichever path produced the
content (ClaudeAuthorProvider or this seam), everything downstream
(Story State updates, the Scene-to-Clip Bridge, Phase 2-5's continuity
pipeline) consumes an EpisodeScript/SeasonConcept identically.
"""
from __future__ import annotations

import json
from pathlib import Path

from tools.authoring.author_provider import build_episode_prompt, build_season_concept_prompt
from tools.authoring.schemas import EpisodeScript, SeasonConcept
from tools.authoring.story_state import StoryStateRepo


def write_episode_author_request(
    root: str | Path,
    *,
    episode_id: str,
    season_id: str,
    theme: str,
    language: str,
    target_age: str,
    premise: str,
    cast_character_ids: list[str],
    location_id: str | None,
    episode_duration_minutes: int,
) -> Path:
    root = Path(root)
    prompt = build_episode_prompt(
        root, episode_id=episode_id, season_id=season_id, theme=theme, language=language,
        target_age=target_age, premise=premise, cast_character_ids=cast_character_ids,
        location_id=location_id, episode_duration_minutes=episode_duration_minutes,
    )
    out_dir = root / "continuity" / "author_requests" / season_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{episode_id}_prompt.txt"
    out_path.write_text(prompt, encoding="utf-8")
    return out_path


def write_season_concept_request(
    root: str | Path, *, season_id: str, theme: str, episode_count: int,
    episode_duration_minutes: int, language: str, target_age: str,
) -> Path:
    root = Path(root)
    prompt = build_season_concept_prompt(
        theme=theme, episode_count=episode_count, episode_duration_minutes=episode_duration_minutes,
        language=language, target_age=target_age,
    )
    out_dir = root / "continuity" / "author_requests" / season_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "season_concept_prompt.txt"
    out_path.write_text(prompt, encoding="utf-8")
    return out_path


def register_authored_episode(root: str | Path, season_id: str, episode_data: dict) -> Path:
    """episode_data is a dict matching schemas.EpisodeScript's shape --
    whatever produced it (a human pasting a model's JSON response, or
    ClaudeAuthorProvider's output serialized). Validates it parses as a
    real EpisodeScript, saves it, and applies its story_updates to Story
    State -- the same story_updates the author explicitly declared, not
    anything inferred."""
    root = Path(root)
    episode = EpisodeScript.from_dict(episode_data)
    out_dir = root / "continuity" / "authored_episodes"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{episode.episode_id}.json"
    out_path.write_text(json.dumps(episode.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if episode.story_updates:
        StoryStateRepo(root).apply_episode_updates(season_id, episode.episode_id, episode.story_updates)

    return out_path


def register_season_concept(root: str | Path, concept_data: dict) -> Path:
    root = Path(root)
    concept = SeasonConcept.from_dict(concept_data)
    out_dir = root / "continuity" / "season_concepts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{concept.season_id}.json"
    out_path.write_text(json.dumps(concept.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out_path


def load_authored_episode(root: str | Path, episode_id: str) -> EpisodeScript | None:
    path = Path(root) / "continuity" / "authored_episodes" / f"{episode_id}.json"
    if not path.exists():
        return None
    return EpisodeScript.from_dict(json.loads(path.read_text(encoding="utf-8")))


def load_season_concept(root: str | Path, season_id: str) -> SeasonConcept | None:
    path = Path(root) / "continuity" / "season_concepts" / f"{season_id}.json"
    if not path.exists():
        return None
    return SeasonConcept.from_dict(json.loads(path.read_text(encoding="utf-8")))
