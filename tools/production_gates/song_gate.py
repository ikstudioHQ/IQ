"""
tools/production_gates/song_gate.py

Real defect found in production, confirmed reproducible: episodes could
declare song.included=True with only a `lyrics_theme` (a prose
description of what the song is ABOUT) and no actual lyrics -- the
finished script would say "Amira sings softly... Zayd joins in on the
chorus" with no chorus text anywhere, and every clip in that scene had
music={}. Nothing in the pipeline required a song to actually exist.

This gate is narrow and specific: if included=True, `lyrics` must be
real, substantial text -- not empty, not just a restatement of
lyrics_theme. It does not judge song quality, only that a song exists
at all when one was claimed.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from tools.authoring.schemas import EpisodeScript

MIN_LYRICS_WORDS = 15


def song_gate_check(root, episode):
    root = Path(root)
    findings = []
    song = episode.song

    if song and song.get("included"):
        lyrics = (song.get("lyrics") or "").strip()
        if not lyrics:
            findings.append({
                "issue": "song_included_without_lyrics",
                "message": (
                    f"Episode {episode.episode_id} declares song.included=true with no "
                    f"song.lyrics -- lyrics_theme ('{(song.get('lyrics_theme') or '')[:80]}...') is a "
                    f"description of the song, not the song itself. A scene describing characters "
                    f"singing with no actual written lyrics is not a real song."
                ),
                "severity": "error",
            })
        elif len(lyrics.split()) < MIN_LYRICS_WORDS:
            findings.append({
                "issue": "song_lyrics_too_short",
                "message": (
                    f"Episode {episode.episode_id}'s song.lyrics is only "
                    f"{len(lyrics.split())} words -- too short to be real verse/chorus content "
                    f"(minimum {MIN_LYRICS_WORDS})."
                ),
                "severity": "error",
            })
        elif lyrics.strip() == (song.get("lyrics_theme") or "").strip():
            findings.append({
                "issue": "song_lyrics_same_as_theme",
                "message": (
                    f"Episode {episode.episode_id}'s song.lyrics is identical to lyrics_theme -- "
                    f"the theme description was copied in rather than real lyrics being written."
                ),
                "severity": "error",
            })

    status = "BLOCKED" if any(f["severity"] == "error" for f in findings) else "PASS"
    result = {
        "episode_id": episode.episode_id, "status": status, "findings": findings,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
    out_path = root / "continuity" / "song_gate" / f"{episode.episode_id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def count_songs_in_season(episodes):
    """A real, existence-checked song count -- counts episodes whose song
    actually HAS lyrics, not just included=True."""
    return sum(
        1 for ep in episodes
        if ep.song and ep.song.get("included") and (ep.song.get("lyrics") or "").strip()
    )
