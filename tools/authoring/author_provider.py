"""
tools/authoring/author_provider.py

Mirrors the Provider Adapter pattern from tools/providers/base.py:
an abstract interface plus prompt/request-building logic that's
provider-independent, so a real author (Claude, Gemini, a human) can
be swapped in without touching anything that consumes its output.

Prompt construction pulls REAL data: character bibles (Phase 2),
environment bibles (Phase 2/3), open Story State threads (this phase),
and safety restrictions (phase2/data/safety/*.json, reused exactly as
Phase 4's safety_check.py reuses it -- not re-derived, not invented).
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from tools.authoring.schemas import EPISODE_SCRIPT_JSON_SCHEMA_HINT, EpisodeScript, SeasonConcept
from tools.authoring.story_state import StoryStateRepo
from tools.production_gates.islamic_gate import eligible_sources_prompt_block


class AuthorProvider(ABC):
    @abstractmethod
    def author_episode(self, prompt: str) -> EpisodeScript:
        """Given a fully-assembled prompt (see build_episode_prompt), return
        a real, original EpisodeScript. Implementations decide HOW the
        content gets written (a live API call, a human, anything) -- this
        interface only defines the contract."""
        ...

    @abstractmethod
    def author_season_concept(self, prompt: str) -> SeasonConcept:
        ...


def _load_character_summaries(root: Path, character_ids: list[str]) -> list[dict]:
    summaries = []
    for cid in character_ids:
        path = root / "continuity" / "character_bible" / f"{cid}.json"
        if not path.exists():
            continue
        bible = json.loads(path.read_text(encoding="utf-8"))
        summaries.append({
            "character_id": cid,
            "canonical_name": bible.get("canonical_name"),
            "role_relation": bible.get("role_relation"),
            "personality_voice": bible.get("voice", {}).get("voice_profile_text"),
            "relationships": bible.get("relationships", []),
        })
    return summaries


def _load_environment_summary(root: Path, location_id: Optional[str]) -> Optional[dict]:
    if not location_id:
        return None
    path = root / "continuity" / "environment_bible" / f"{location_id}.json"
    if not path.exists():
        return None
    bible = json.loads(path.read_text(encoding="utf-8"))
    return {
        "location_id": location_id,
        "display_name": bible.get("display_name"),
        "canonical_description": bible.get("canonical_description"),
        "continuity_notes": bible.get("continuity_notes"),
    }


def _load_safety_constraints(root: Path) -> list[str]:
    constraints = []
    path = root / "phase2" / "data" / "safety" / "content_restrictions.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        for r in data.get("restrictions", []):
            if r["level"] in ("NEVER_GENERATE", "REVIEW_REQUIRED"):
                constraints.append(f"{r['canonical_name']} ({r['category']}, {r['level']})")
    path2 = root / "phase2" / "data" / "safety" / "content_scene_safety_registry.json"
    if path2.exists():
        data2 = json.loads(path2.read_text(encoding="utf-8"))
        for r in data2.get("rules", []):
            if r["decision"] in ("BLOCK", "REVIEW_REQUIRED"):
                constraints.append(f"{r['description']} ({r['category']}, {r['decision']})")
    return constraints


def build_episode_prompt(
    root: str | Path,
    *,
    episode_id: str,
    season_id: str,
    theme: str,
    language: str,
    target_age: str,
    premise: str,
    cast_character_ids: list[str],
    location_id: Optional[str],
    episode_duration_minutes: int,
) -> str:
    """Assembles the full authoring request. This is the actual prompt a
    real model call sends, and also exactly what the manual seam writes
    to a file for external execution -- same content either way, so
    there's no discrepancy between the "automatic" and "manual" paths."""
    root = Path(root)
    characters = _load_character_summaries(root, cast_character_ids)
    environment = _load_environment_summary(root, location_id)
    safety_constraints = _load_safety_constraints(root)

    story_repo = StoryStateRepo(root)
    relevant_threads = []
    for cid in cast_character_ids:
        relevant_threads.extend(story_repo.load(season_id).threads_involving(cid))
    seen = set()
    relevant_threads = [t for t in relevant_threads if not (t["thread_id"] in seen or seen.add(t["thread_id"]))]

    parts = [
        "You are writing an original episode for a children's Islamic educational animated series.",
        "",
        f"SEASON THEME: {theme}",
        f"EPISODE PREMISE: {premise}",
        f"LANGUAGE: {language}",
        f"TARGET AGE: {target_age}",
        f"TARGET DURATION: approximately {episode_duration_minutes} minutes",
        "",
        "CAST (use ONLY these character_ids, stay true to each character's established voice and relationships):",
        json.dumps(characters, indent=2),
    ]
    if environment:
        parts += ["", "PRIMARY LOCATION (use this location_id if the scene is here; the room's physical "
                       "details below are canon and must not be contradicted):", json.dumps(environment, indent=2)]
    if relevant_threads:
        parts += [
            "", "OPEN STORY THREADS involving this cast -- maintain continuity. If a thread naturally "
                 "resolves or gets referenced in this episode, say so in story_updates. Do not resolve a "
                 "thread that doesn't naturally come up; open threads are allowed to stay open.",
            json.dumps(relevant_threads, indent=2),
        ]
    parts += [
        "", "CONTENT RESTRICTIONS -- never write content matching any of these categories:",
        json.dumps(safety_constraints, indent=2),
        "",
        eligible_sources_prompt_block(root),
        "",
        "SONGS: include a song ONLY if it emerges naturally from the story (e.g. a genuine emotional "
        "high point, a traditional moment like bedtime or a celebration). Do not force a song into every "
        "episode. State your reasoning either way in the song field.",
        "",
        "Write real, original dialogue and action -- not generic filler. Every scene should feel specific "
        "to this premise and these characters, not interchangeable with any other episode.",
        "",
        EPISODE_SCRIPT_JSON_SCHEMA_HINT,
    ]
    return "\n".join(parts)


def build_season_concept_prompt(
    *, theme: str, episode_count: int, episode_duration_minutes: int, language: str, target_age: str,
) -> str:
    return "\n".join([
        f"You are planning a {episode_count}-episode season of a children's Islamic educational animated series.",
        f"THEME: {theme}", f"LANGUAGE: {language}", f"TARGET AGE: {target_age}",
        f"EPISODE DURATION: approximately {episode_duration_minutes} minutes each",
        "",
        f"Propose one premise per episode, forming a real season arc (not {episode_count} disconnected "
        "episodes) -- early episodes should introduce elements later episodes build on.",
        "",
        "Return ONLY valid JSON: {\"season_id\": \"string\", \"theme\": \"string\", \"language\": \"string\", "
        "\"target_age\": \"string\", \"episode_count\": number, \"episode_duration_minutes\": number, "
        "\"premises\": [{\"episode_id\": \"string\", \"title\": \"string\", \"premise\": \"string\", "
        "\"arc_position\": \"string\"}]}",
    ])
