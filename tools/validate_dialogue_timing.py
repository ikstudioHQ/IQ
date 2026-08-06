#!/usr/bin/env python3
"""Real, executable dialogue-duration validator for Gemini clips.
Extends the existing tooling -- not a new engine, just a calculation
the export layer needs before packaging any clip with dialogue."""
import json, sys

WORDS_PER_MINUTE = {"slow": 110, "medium": 150, "fast": 190}

def estimate_speech_duration(text, pace="medium"):
    word_count = len(text.split())
    wpm = WORDS_PER_MINUTE.get(pace, 150)
    return round(word_count / wpm * 60, 2)

def validate_clip_timing(dialogue, dialogue_start, dialogue_end, pace="medium"):
    word_count = len(dialogue.split())
    available = round(dialogue_end - dialogue_start, 2)
    estimated = estimate_speech_duration(dialogue, pace)
    if estimated <= available:
        status = "PASS"
    elif estimated <= available * 1.15:
        status = "REVIEW_REQUIRED"  # close, a real actor/TTS might still fit it
    else:
        status = "SPLIT_REQUIRED"
    return {
        "dialogue": dialogue, "word_count": word_count, "pace": pace,
        "target_start": dialogue_start, "target_end": dialogue_end,
        "available_seconds": available, "estimated_speech_duration": estimated,
        "timing_status": status,
    }

if __name__ == "__main__":
    # self-test against the real test_gemini_scene clips
    tests = [
        ("Alhamdulillah, thank you for helping me carry these!", 2.5, 5.8, "slow-medium"),
        ("Of course! That's what family is for.", 2.0, 5.2, "medium"),
    ]
    for text, start, end, pace in tests:
        r = validate_clip_timing(text, start, end, pace if pace in WORDS_PER_MINUTE else "medium")
        print(json.dumps(r, indent=2))
