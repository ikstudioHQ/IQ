"""
tools/authoring/schemas.py

The structured contract authored content must fill in. Deliberately
structured (not free prose) for two reasons: (1) Story State updates
come from the author's own explicit declaration, not inference from
prose -- see story_state.py's docstring; (2) the Scene-to-Clip Bridge
needs beat-level boundaries (dialogue line vs. action vs. camera note)
to cut clips at natural boundaries rather than blind character-count
slicing, per Phase 6's explicit requirement.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class Beat:
    """The smallest unit the Scene-to-Clip Bridge will ever split on --
    a beat is NEVER divided across two clips."""
    beat_id: str
    kind: str  # "action" | "dialogue" | "camera_note"
    text: str
    character_id: Optional[str] = None  # required for kind="dialogue"
    emotion: Optional[str] = None
    camera_hint: Optional[str] = None  # a Camera Bible scene_type, or None to inherit
    estimated_seconds: Optional[float] = None  # None -> bridge estimates from text


@dataclass
class Scene:
    scene_id: str
    location_id: Optional[str]
    characters_present: list[str]
    props_visible: list[str] = field(default_factory=list)
    environment_overrides: dict = field(default_factory=dict)  # e.g. {"time_of_day": "evening"} for a deliberate story-driven change
    beats: list[dict] = field(default_factory=list)  # Beat.__dict__ entries


@dataclass
class SongDecision:
    included: bool
    reason: str  # required either way -- "no" needs a reason too, so a lazy omission is visible, not a default
    lyrics_theme: Optional[str] = None  # a THEME/description, not the song itself -- see `lyrics` below
    placement_scene_id: Optional[str] = None
    # Real production found `lyrics_theme` alone was letting "included: true"
    # pass with no actual song ever written -- a prose paragraph describing
    # what the song is about is not a song. `lyrics` is the real verse/
    # chorus text; the Song Gate (tools/production_gates/song_gate.py)
    # requires this to be non-empty whenever included=True.
    lyrics: Optional[str] = None


@dataclass
class EpisodeScript:
    episode_id: str
    title: str
    theme: str
    language: str
    target_age: str
    scenes: list[dict] = field(default_factory=list)  # Scene.__dict__ entries
    song: Optional[dict] = None  # SongDecision.__dict__, or None if not yet decided
    story_updates: dict = field(default_factory=dict)  # see StoryStateRepo.apply_episode_updates docstring

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "EpisodeScript":
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class EpisodePremise:
    episode_id: str
    title: str
    premise: str
    arc_position: str  # e.g. "introduces the season's central lesson", "mid-season complication", "season finale"


@dataclass
class SeasonConcept:
    season_id: str
    theme: str
    language: str
    target_age: str
    episode_count: int
    episode_duration_minutes: int
    premises: list[dict] = field(default_factory=list)  # EpisodePremise.__dict__ entries

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SeasonConcept":
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in known})


EPISODE_SCRIPT_JSON_SCHEMA_HINT = """
Return ONLY valid JSON matching this shape (no markdown fences, no commentary):
{
  "episode_id": "string",
  "title": "string",
  "theme": "string",
  "language": "string",
  "target_age": "string",
  "scenes": [
    {
      "scene_id": "string",
      "location_id": "string or null (a real location_id from the Environment Bible provided, or null for a new place)",
      "characters_present": ["character_id", ...],
      "props_visible": ["prop_id", ...],
      "environment_overrides": {"time_of_day": "evening"},
      "beats": [
        {"beat_id": "string", "kind": "action|dialogue|camera_note",
         "text": "string", "character_id": "character_id or null",
         "emotion": "string or null", "camera_hint": "string or null",
         "estimated_seconds": number or null}
      ]
    }
  ],
  "song": {"included": true/false, "reason": "string", "lyrics_theme": "string or null (a short THEME description, not the song itself)", "lyrics": "string or null -- the ACTUAL verse/chorus text if included=true; REQUIRED and must be real written lyrics, not a description, whenever included is true", "placement_scene_id": "string or null"},
  "story_updates": {
    "new_threads": [{"kind": "promise|open_thread|secret|goal|running_joke|lesson|conflict",
                      "description": "string", "involved_characters": ["character_id", ...]}],
    "resolved_thread_ids": ["thread_id", ...],
    "resolution_notes": {"thread_id": "how it was resolved"},
    "referenced_thread_ids": ["thread_id", ...],
    "emotional_notes": [{"character_id": "character_id", "note": "string"}]
  }
}
"""
