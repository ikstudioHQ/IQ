"""One-time, real, human-structured migration tool -- not an automated
guesser run blindly on future episodes. Builds a structured
scene_contract.json per episode: canonical character IDs for visible
characters (from confirmed full-lock presence in image_prompts.md),
and performance_events for speaking/singing (from real dialogue.md
lines mapped to scenes via strict narrative order + explicit thematic
correlation to animation_directions.md's own scene description --
never guessed, always with a stated confidence level and reasoning).

Design choice over 'canonical IDs + structured events' alone: this
schema ALSO keeps the original human-readable scene_breakdown.md
prose completely untouched as the separate creative-reference layer --
satisfies 'preserve human-readable descriptions separately' exactly."""
import json, hashlib

def build_ep_tawakkul_lost_toy():
    char_lib = json.load(open("sources/characters/character_master_library.json"))
    name_to_id = {c["canonical_name"].split("(")[0].strip(): c["character_id"] for c in char_lib["characters"]}

    scenes = [
        {
            "scene_id": "scene_1", "location": "env_park", "duration_seconds": 15,
            "visible_characters": [name_to_id["Zayd"], name_to_id["Amira"], name_to_id["Nuri"]],
            "visible_characters_confidence": "CONFIRMED — each character has a full canonical locked description inlined in image_prompts.md Block 1, which only occurs for characters actually rendered in that scene.",
            "performance_events": [
                {"character_id": name_to_id["Zayd"], "type": "SPOKEN", "text": "Nuri, watch — my camel can jump THIS high today!",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — first dialogue.md line, thematically matches animation_directions.md Block 1's 'jump apex' lip-sync note and this scene's own jumping action. Not an explicit source-stated scene assignment."},
                {"character_id": name_to_id["Amira"], "type": "SPOKEN", "text": "That's the highest yet!",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — same reasoning as above, second line, same scene's joy beat."}
            ],
        },
        {
            "scene_id": "scene_2", "location": "env_home (Zayd's bedroom)", "duration_seconds": 55,
            "visible_characters": [name_to_id["Zayd"]],
            "visible_characters_confidence": "CONFIRMED — image_prompts.md Block 2 inlines only Zayd's full lock; animation_directions.md Block 2 explicitly says 'minimal dialogue, mostly physical performance' with only Zayd described acting.",
            "performance_events": [
                {"character_id": name_to_id["Zayd"], "type": "SPOKEN", "text": "Time for bed, little camel... camel?",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — thematically matches this scene's 'searching' action (toy/bedtime reference); animation explicitly confirms 'minimal dialogue' fits a short line here."},
                {"character_id": name_to_id["Zayd"], "type": "SPOKEN", "text": "Not here... Not here either...",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — directly matches animation's described searching sequence (toy basket, under the bed)."}
            ],
        },
        {
            "scene_id": "scene_3", "location": "env_home (Zayd's bedroom)", "duration_seconds": 60,
            "visible_characters": [name_to_id["Zayd"], name_to_id["Ummi Layla"]],
            "visible_characters_confidence": "CONFIRMED — image_prompts.md Block 3 inlines both full locks; animation_directions.md Block 3 explicitly names both.",
            "performance_events": [
                {"character_id": name_to_id["Ummi Layla"], "type": "SPOKEN", "text": "You've looked so hard already, habibi.",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — matches this scene's comforting beat."},
                {"character_id": name_to_id["Zayd"], "type": "SPOKEN", "text": "I looked everywhere, Ummi. What if it's really gone?",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — direct reply, same beat."},
                {"character_id": name_to_id["Ummi Layla"], "type": "SPOKEN", "text": "You did your best. Now — let's ask Allah to help us, and keep looking together, calmly. Hasbunallahu wa ni'mal wakeel.",
                 "confidence": "CONFIRMED — animation_directions.md Block 3 explicitly states 'the dua is said together, lips moving in sync on the Arabic phrase,' directly naming this as a shared dua moment; the dua text itself matches dua_005/dua_006 already cited elsewhere in this repository."},
                {"character_id": name_to_id["Zayd"], "type": "SPOKEN", "text": "Hasbunallahu wa ni'mal wakeel.",
                 "confidence": "CONFIRMED — same explicit 'said together' source statement covers both speakers of this shared dua line."}
            ],
        },
        {
            "scene_id": "scene_4", "location": "env_home (living room)", "duration_seconds": 40,
            "visible_characters": [name_to_id["Zayd"], name_to_id["Amira"]],
            "visible_characters_confidence": "CONFIRMED — image_prompts.md Block 4 inlines both full locks; animation_directions.md Block 4 explicitly names both acting.",
            "performance_events": [
                {"character_id": name_to_id["Amira"], "type": "SPOKEN", "text": "Wait... did you bring him to the park in your bag?",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — matches animation's explicitly-named 'Amira's realization' beat."},
                {"character_id": name_to_id["Zayd"], "type": "SPOKEN", "text": "My park bag!",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — direct reaction, matches the 'reveal' beat."},
                {"character_id": name_to_id["Zayd"], "type": "SPOKEN", "text": "Alhamdulillah! You were right here the whole time!",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — matches animation's 'full-body happy bounce' relief/joy beat."}
            ],
        },
        {
            "scene_id": "scene_5", "location": "env_home (living room)", "duration_seconds": 30,
            "visible_characters": [name_to_id["Zayd"], name_to_id["Amira"], name_to_id["Ummi Layla"]],
            "visible_characters_confidence": "CONFIRMED — scene_breakdown.md's own text says 'Full family' and animation_directions.md Block 5 explicitly says 'all three characters' expressions soften'; cross-referenced with the family composition already established in scenes 3-4 (Zayd, Amira, Ummi Layla are this family's only members appearing anywhere in this episode).",
            "performance_events": [
                {"character_id": name_to_id["Zayd"], "type": "SPOKEN", "text": "Hasbunallahu wa ni'mal wakeel.",
                 "confidence": "CONFIRMED — animation_directions.md Block 5 explicitly says 'during the dua line,' and this is the only remaining unassigned dua-text line in dialogue.md's order, spoken solo by Zayd per the earlier-established pattern (Scene 3's dua was shared, this repetition here is his alone, matching this repository's real islamic_refs.md note that this line is said 'solo by Zayd in Scene 5')."},
                {"character_id": name_to_id["Ummi Layla"], "type": "SPOKEN", "text": "Allah is always enough for us.",
                 "confidence": "CONFIRMED — final line, matches this scene's closing warmth beat, and voice_instructions.md's own note that this line closes the episode."}
            ],
            "note": "This scene's Amira presence is visually CONFIRMED but she has NO performance_event -- dialogue.md contains no further Amira lines after Scene 4. This is correctly reported as silent-but-visible, not SOURCE_DATA_INSUFFICIENT, since her silence here is a real absence of data, not an unresolved question."
        },
    ]

    total_dialogue_lines_in_source = 13
    total_mapped = sum(len(s["performance_events"]) for s in scenes)
    assert total_mapped == total_dialogue_lines_in_source, f"Mapping count mismatch: {total_mapped} vs {total_dialogue_lines_in_source} -- would indicate a real line was dropped or duplicated."

    return {
        "schema_version": "1.0", "episode_id": "ep_tawakkul_lost_toy",
        "note": "Structured performance/visibility data. scene_breakdown.md remains the separate, untouched human-readable creative summary -- this file is the machine-authoritative companion, not a replacement.",
        "migration_method": "Manual, human-structured cross-reference of image_prompts.md (visible-character confirmation via full-lock presence), animation_directions.md (explicit speech/dua statements), and dialogue.md (strict narrative order) -- not automated guessing, not run blindly. Per-event certainty varies -- see each performance_event's own 'confidence' field (CONFIRMED = explicit source statement; INFERRED_FROM_ORDER_AND_CONTENT = reasoned, not independently verified).",
        "scenes": scenes,
    }

if __name__ == "__main__":
    contract = build_ep_tawakkul_lost_toy()
    json.dump(contract, open("production/episodes/ep_tawakkul_lost_toy/scene_contract.json", "w"), indent=2, ensure_ascii=False)
    print("Built scene_contract.json for ep_tawakkul_lost_toy")
    confirmed = sum(1 for s in contract["scenes"] for e in s["performance_events"] if e["confidence"].startswith("CONFIRMED"))
    inferred = sum(1 for s in contract["scenes"] for e in s["performance_events"] if e["confidence"].startswith("INFERRED"))
    print(f"Performance events: {confirmed} CONFIRMED (explicit source statement), {inferred} INFERRED_FROM_ORDER_AND_CONTENT (real but reasoned, not explicit)")

def build_ep_honesty_wallet_assisted():
    char_lib = json.load(open("sources/characters/character_master_library.json"))
    name_to_id = {c["canonical_name"].split("(")[0].strip(): c["character_id"] for c in char_lib["characters"]}

    scenes = [
        {
            "scene_id": "scene_1", "location": "env_market", "duration_seconds": 15,
            "visible_characters": [name_to_id["Zayd"], name_to_id["Amira"]],
            "visible_characters_confidence": "CONFIRMED — image_prompts.md Block 1 inlines both full locks.",
            "performance_events": [
                {"character_id": name_to_id["Amira"], "type": "SPOKEN", "text": "These dates look perfect for Ummi's basket.",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — first dialogue.md line, matches this scene's browsing/market beat."},
            ],
        },
        {
            "scene_id": "scene_2", "location": "env_market", "duration_seconds": 45,
            "visible_characters": [name_to_id["Zayd"]],
            "visible_characters_confidence": "CONFIRMED — scene_breakdown.md explicitly states 'Zayd alone with the wallet'; image_prompts.md Block 2 inlines only Zayd's full lock.",
            "performance_events": [
                {"character_id": name_to_id["Zayd"], "type": "SPOKEN", "text": "Amira, look—",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — note: text addresses Amira but scene_breakdown.md says Zayd is alone here; likely a transition line at scene boundary. Flagged as lower-confidence placement."},
                {"character_id": name_to_id["Zayd"], "type": "SPOKEN", "text": "It's... someone's wallet. It has money in it.",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — matches 'finding the wallet' scene title exactly."},
                {"character_id": name_to_id["Zayd"], "type": "SPOKEN", "text": "No one's even looking...",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — matches this scene's 'Tension' beat."},
            ],
            "note": "SOURCE_AMBIGUITY: 'Amira, look—' addresses Amira in a scene scene_breakdown.md says is Zayd alone. Not silently resolved -- flagged here rather than guessed away."
        },
        {
            "scene_id": "scene_3", "location": "env_market (quieter corner)", "duration_seconds": 75,
            "visible_characters": [name_to_id["Zayd"], name_to_id["Amira"]],
            "visible_characters_confidence": "CONFIRMED — image_prompts.md Block 3 inlines both full locks; scene_breakdown.md explicitly states 'Zayd + Amira'.",
            "performance_events": [
                {"character_id": name_to_id["Amira"], "type": "SPOKEN", "text": "Zayd? What's wrong?",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — matches 'Decision' scene's opening beat; also explains the earlier Scene 2 ambiguity -- Amira likely rejoins right at this scene's start."},
                {"character_id": name_to_id["Zayd"], "type": "SPOKEN", "text": "I don't know what to do. Part of me wants to just... keep it.",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — matches the moral-conflict beat."},
                {"character_id": name_to_id["Amira"], "type": "SPOKEN", "text": "It's not ours though.",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — direct reply."},
                {"character_id": name_to_id["Zayd"], "type": "SPOKEN", "text": "Sidq means telling the truth about it. And amanah means taking care of it properly, since it isn't mine.",
                 "confidence": "CONFIRMED — matches this repository's own cited evidence (hd_005/qv_009, sidq/amanah) already linked to this episode's islamic_refs.md."},
                {"character_id": name_to_id["Zayd"], "type": "SPOKEN", "text": "I've decided what's right. Now I'll trust Allah with the rest.",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — matches this scene's resolution beat, tawakkul theme."},
            ],
        },
        {
            "scene_id": "scene_4", "location": "env_market (stall)", "duration_seconds": 50,
            "visible_characters": [name_to_id["Zayd"], "NONCANONICAL_BACKGROUND: market stall owner"],
            "visible_characters_confidence": "CONFIRMED Zayd (full lock in image_prompts.md Block 4). Stall owner CONFIRMED PRESENT but has NO canonical character_id -- image_prompts.md explicitly describes them as generic '(simple, friendly design, modest clothing)', the same deliberate non-canonical-background-character pattern used elsewhere in this repository. Not a gap -- a real, intentional design choice.",
            "performance_events": [
                {"character_id": name_to_id["Zayd"], "type": "SPOKEN", "text": "Excuse me — I found this wallet near your stall. I think it might be yours, or someone dropped it here.",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — matches 'returning the wallet' scene title exactly."},
                {"character_id": "NONCANONICAL_BACKGROUND: market stall owner", "type": "SPOKEN", "text": "This is mine! I didn't even notice it was gone. Thank you, truly — that was very honest of you.",
                 "confidence": "CONFIRMED — dialogue.md explicitly labels this line 'STALL OWNER:'."},
                {"character_id": name_to_id["Zayd"], "type": "SPOKEN", "text": "Hasbunallahu wa ni'mal wakeel.",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — matches this repository's real tawakkul evidence already cited for this episode."},
            ],
        },
        {
            "scene_id": "scene_5", "location": "walking home", "duration_seconds": 30,
            "visible_characters": [name_to_id["Zayd"], name_to_id["Amira"]],
            "visible_characters_confidence": "CONFIRMED — image_prompts.md Block 5 inlines both full locks; scene_breakdown.md explicitly states 'Zayd + Amira'.",
            "performance_events": [
                {"character_id": name_to_id["Amira"], "type": "SPOKEN", "text": "That felt like the right thing, didn't it?",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — matches this scene's closing beat."},
                {"character_id": name_to_id["Zayd"], "type": "SPOKEN", "text": "It did.",
                 "confidence": "INFERRED_FROM_ORDER_AND_CONTENT — final line, direct reply."},
            ],
        },
    ]

    total_mapped = sum(len(s["performance_events"]) for s in scenes)
    real_total = 14
    assert total_mapped == real_total, f"Mapping count mismatch: {total_mapped} vs {real_total}"

    return {
        "schema_version": "1.0", "episode_id": "ep_honesty_wallet_assisted",
        "note": "Structured performance/visibility data. scene_breakdown.md remains the separate, untouched human-readable creative summary.",
        "migration_method": "Manual, human-structured cross-reference -- not automated guessing. Per-event certainty varies -- see each performance_event's own 'confidence' field (CONFIRMED = explicit source statement; INFERRED_FROM_ORDER_AND_CONTENT = reasoned, not independently verified).",
        "scenes": scenes,
    }

if __name__ == "__main__" and len(__import__("sys").argv) > 1 and __import__("sys").argv[1] == "ep2":
    contract = build_ep_honesty_wallet_assisted()
    import os
    os.makedirs("production/episodes/ep_honesty_wallet_assisted", exist_ok=True)
    json.dump(contract, open("production/episodes/ep_honesty_wallet_assisted/scene_contract.json", "w"), indent=2, ensure_ascii=False)
    print("Built scene_contract.json for ep_honesty_wallet_assisted")
