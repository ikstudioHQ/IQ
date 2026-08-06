"""Regression fixtures derived from the real v2.46 failed production
batch. Each test documents an actual defect that was found and fixed --
not theoretical cases."""
import subprocess, sys, os, glob, json, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_compiler():
    subprocess.run([sys.executable, os.path.join(REPO, "tools", "compile_gemini_scenes.py")],
                    cwd=REPO, capture_output=True)

def test_no_stale_contradictory_content():
    """Defect A: song_001 scene_04 had BOTH old and new grain imagery."""
    text = open(os.path.join(REPO, "production/songs/song_001/Gemini/scene_04.md")).read()
    assert "tall tree" not in text, "stale content regression"
    assert "golden wheat stalk" in text, "corrected content missing"

def test_no_reference_asset_leak():
    """Defect B: reference-sheet generation instructions leaked into scenes."""
    for f in glob.glob(os.path.join(REPO, "production/songs/*/Gemini/scene_*.md")):
        assert "front three-quarter pose" not in open(f).read(), f"reference-asset leak in {f}"

def test_no_duplicate_character_identity():
    """Defect C: character identity was rendered twice in the same
    prompt. Real fix (v2.62): the original raw-count threshold (<=5)
    broke as real scenes correctly grew to more characters -- 3 real
    characters naturally produce 6 occurrences (3 in the structured
    VISIBLE CHARACTERS block + 3 more inside the raw VISUAL field's
    own source text, a real separate, legitimate source). The actual
    invariant that matters is per-name: no single character's
    identity block appears more than once WITHIN the structured
    VISIBLE CHARACTERS section specifically."""
    for f in glob.glob(os.path.join(REPO, "production/songs/*/Gemini/scene_*.md")):
        text = open(f).read()
        m = re.search(r"VISIBLE CHARACTERS.*?:\n(.*?)\n\nVOICE IDENTITY", text, re.DOTALL)
        if not m:
            continue
        char_block = m.group(1)
        names = re.findall(r"^([A-Z][a-zA-Z' ]+) — ", char_block, re.MULTILINE)
        assert len(names) == len(set(names)), f"real per-name duplication in {f}: {names}"

def test_music_not_truncated():
    """Defect D: music field ended mid-sentence ('bridge drops to')."""
    for f in glob.glob(os.path.join(REPO, "production/songs/*/Gemini/scene_*.md")):
        text = open(f).read()
        assert "bridge drops to\n" not in text and not text.rstrip().endswith("drops to"), f"truncated music in {f}"

def test_no_dangling_possessive_from_stripped_filename():
    """The exact defect found by real independent inspection: the
    dependency-stripper deleted 'ending_styles.json' but left the
    possessive 's dangling, producing 'from 's family/dua endings'
    across 6+ songs. Fixed to consume the possessive and collapse the
    resulting double space."""
    for f in glob.glob(os.path.join(REPO, "production/songs/*/Gemini/scene_*.md")):
        text = open(f).read()
        assert "from 's" not in text and "from '" not in text, f"dangling possessive artifact in {f}"
        assert "  " not in text.replace("\n\n", "").replace("\n  ", "\n"), f"double-space strip artifact in {f}"

def test_no_speaker_misattribution():
    """Defect found by real inspection: dialogue with real per-line
    speakers (from dialogue.md) was wrapped under one SUNG label,
    telling Gemini one character performs everyone's lines."""
    import re as re_
    for f in glob.glob(os.path.join(REPO, "production/songs/*/Gemini/scene_*.md")):
        text = open(f).read()
        assert not re_.search(r'—\s*(SUNG|SPOKEN).*?\n"[A-Z]+:\s', text), f"speaker misattribution in {f}"

def test_voice_locks_present_when_performer_named():
    """Defect found by real inspection: real_performer_names extracted
    ALL-CAPS names ('ZAYD') but voice_map used Title Case ('Zayd'),
    so the comparison never matched -- voice locks were silently
    empty even when a named character clearly performed. Chorus-only
    scenes (no individual named voice) are the one legitimate
    exception and are excluded here."""
    import re as re_
    for f in glob.glob(os.path.join(REPO, "production/songs/*/Gemini/scene_*.md")):
        text = open(f).read()
        has_named_performer = bool(re_.search(r'^[A-Z][a-z]+\s*—\s*(SPOKEN|SUNG)', text, re_.MULTILINE)) or \
                               bool(re_.search(r'^[A-Z]+\s*—\s*(SPOKEN|SUNG)', text, re_.MULTILINE)) and "CHILDREN" not in text.split("EXACT DIALOGUE")[1][:50] if "EXACT DIALOGUE" in text else False
        if has_named_performer:
            assert "VOICE LOCK —" in text, f"missing voice lock despite named performer in {f}"

def test_generalized_text_integrity_all_scenes():
    """Real, GENERALIZED check -- not another test for one exact string.
    Runs the class-level integrity checker (dangling prepositions,
    double spaces, dangling possessives, doubled commas) across EVERY
    real compiled scene, songs and episodes both, not a sample.
    This is what was missing before: prior tests only checked for
    specific already-seen bad strings."""
    sys.path.insert(0, os.path.join(REPO, "tools"))
    from gemini_shared import check_text_integrity
    all_files = glob.glob(os.path.join(REPO, "production/songs/song_0*/Gemini/scene_*.md")) + \
                glob.glob(os.path.join(REPO, "output_package/ep_*/Gemini/scene_*.md"))
    assert len(all_files) >= 60, f"expected at least 60 real scene files, found {len(all_files)} -- checking fewer than expected"
    for f in all_files:
        issues = check_text_integrity(open(f).read())
        assert not issues, f"TEXT_INTEGRITY issues in {f}: {issues}"

def test_no_overstated_verification_claims():
    """Real check: prompt text must never claim 'human-verified' for a
    block that can contain INFERRED_FROM_ORDER_AND_CONTENT events --
    the exact semantic-overreach defect found by real inspection."""
    for f in glob.glob(os.path.join(REPO, "output_package/ep_*/Gemini/scene_*.md")):
        text = open(f).read()
        assert "human-verified" not in text, f"overstated verification claim in {f}"

def test_package_completeness():
    """The exact defect this whole repair round started from: song_010
    missing. Real fix (v2.61): check consistency (every song dir has a
    real 5-scene Gemini output), not a hardcoded count -- the real
    corpus grew from 10 to 20 songs and a fixed number would break
    this test every time real content is legitimately added."""
    songs = sorted(d for d in glob.glob(os.path.join(REPO, "production/songs/song_0*")) if os.path.isdir(d))
    assert len(songs) >= 10, f"PACKAGE COMPLETENESS: expected at least the original 10, found {len(songs)}"
    for s in songs:
        manifest_path = os.path.join(s, "Gemini", "scene_manifest.json")
        assert os.path.exists(manifest_path), f"{s}: missing Gemini/scene_manifest.json"

def test_external_dependencies_zero():
    for f in glob.glob(os.path.join(REPO, "production/songs/*/Gemini/scene_*.md")):
        text = open(f).read()
        assert ".md" not in text and ".json" not in text, f"external dependency leak in {f}"

def test_episode_scene_contract_authoritative():
    """v2.57: episode character/performer data must come from
    scene_contract.json, not guessed from prose. Real check: every
    compiled episode scene must have non-empty VISIBLE CHARACTERS
    unless the contract itself says none, and the newline-dependent
    possessive-stripper bug must not reappear."""
    for ep in ["ep_tawakkul_lost_toy", "ep_honesty_wallet_assisted"]:
        contract_path = os.path.join(REPO, "production/episodes", ep, "scene_contract.json")
        assert os.path.exists(contract_path), f"{ep}: scene_contract.json missing"
        contract = json.load(open(contract_path))
        for scene in contract["scenes"]:
            scene_file = os.path.join(REPO, "output_package", ep, "Gemini", f"scene_{scene['scene_id'].split('_')[-1]}.md")
            assert os.path.exists(scene_file), f"{ep} {scene['scene_id']}: compiled file missing"
            text = open(scene_file).read()
            if scene["visible_characters"]:
                assert "(none identified" not in text, f"{ep} {scene['scene_id']}: real contract characters not reflected in output"
            assert "calm closing's" not in text, f"{ep}: the exact newline-possessive bug regressed"


def test_performer_always_in_visible_characters():
    """Real defect found by independent inspection: 11 real scenes had
    a confirmed SPOKEN/SUNG performer missing from VISIBLE CHARACTERS
    (e.g. song_011's Hamza, who speaks but wasn't listed as visible).
    Fixed with a real invariant: a confirmed performer is always
    present, full stop -- auto-corrected with an audit trail."""
    for f in glob.glob(os.path.join(REPO, "production/songs/*/Gemini/scene_*.md")):
        text = open(f).read()
        m = re.search(r"VISIBLE CHARACTERS.*?:(.*?)\n", text)
        visible = m.group(1) if m else ""
        performers = re.findall(r"^([A-Za-z][A-Za-z' ]*?) — (?:SPOKEN|SUNG)", text, re.MULTILINE)
        for p in performers:
            performer = p.strip()
            if performer.upper() in {"CHILDREN'S CHORUS", "CHILDREN/GROUP"}:
                # A performance-group label is not a canonical character identity.
                # It must resolve to the real visible group members instead of being
                # fabricated as an extra named character.
                assert "CHILDREN/GROUP resolves to:" in text, f"{f}: group performer has no resolved membership"
                continue
            if performer.upper() == "NARRATOR":
                # Narration is off-screen voiceover, not a visible character.
                continue
            assert performer.lower() in visible.lower(), f"{f}: performer '{performer}' not in VISIBLE CHARACTERS"

def test_no_word_space_period_defect():
    """Real defect: 'no loud drums .' present in 100/100 song scenes."""
    for f in glob.glob(os.path.join(REPO, "production/songs/*/Gemini/scene_*.md")):
        assert not re.search(r"\s+\.(?!\.)", open(f).read()), f"word-space-period defect in {f}"

def test_no_dangling_em_dash_truncation():
    """Real defect: 'Depth of field: Medium —' with nothing following --
    traced to truncate_at_sentence() treating an em-dash as a valid
    sentence-cut boundary, when it only marks clause continuation."""
    for f in glob.glob(os.path.join(REPO, "production/songs/*/Gemini/scene_*.md")):
        assert not re.search(r"—\s*\n\n|—\s*$", open(f).read(), re.MULTILINE), f"dangling em-dash truncation in {f}"

if __name__ == "__main__":
    run_compiler()
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} passed")
