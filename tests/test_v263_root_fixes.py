import importlib.util,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load_module(rel,name):
    spec=importlib.util.spec_from_file_location(name,ROOT/rel); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def current_version():
    return json.loads((ROOT/'repository_manifest.json').read_text())['repository_version']

def test_runtime_compiler_resolves_version_from_authority_not_literal():
    m=load_module('tools/compile_runtime.py','compile_runtime_v263')
    old=Path.cwd()
    try:
        import os; os.chdir(ROOT)
        assert m.get_repo_version()==current_version()
    finally: os.chdir(old)
    assert 'REPO_VERSION = "2.41"' not in (ROOT/'tools/compile_runtime.py').read_text()

def test_fingerprint_matches_live_version_and_file_count():
    fp=json.loads((ROOT/'generated/repository_fingerprint.json').read_text())
    ignored={'.git','__pycache__','.pytest_cache'}
    actual=sum(1 for p in ROOT.rglob('*') if p.is_file() and not any(x in ignored for x in p.parts) and p.name not in {'.protected_snapshot.json','MASTER_PROMPT.md'} and '/Gemini/' not in ('/'+p.relative_to(ROOT).as_posix()) and not (p.suffix.lower()=='.zip' and p.relative_to(ROOT).parts[0]=='output_package'))
    assert fp['repository_version']==current_version()
    assert fp['total_files']==actual

def test_honesty_scene_boundary_is_resolved():
    d=json.loads((ROOT/'production/episodes/ep_honesty_wallet_assisted/scene_contract.json').read_text())
    s1,s2=d['scenes'][:2]
    assert any(e.get('text')=='Amira, look—' for e in s1['performance_events'])
    assert not any(e.get('text')=='Amira, look—' for e in s2['performance_events'])
    assert 'SOURCE_AMBIGUITY' not in json.dumps(d)

def test_confirmed_song_participants_are_in_source_tables():
    s1=(ROOT/'production/songs/song_001/scene_breakdown.md').read_text()
    for n in (2,3,4):
        line=next(x for x in s1.splitlines() if x.startswith(f'| Scene {n} |'))
        assert "Children's Chorus" in line
    s2=(ROOT/'production/songs/song_002/scene_breakdown.md').read_text()
    line=next(x for x in s2.splitlines() if x.startswith('| Scene 1 |'))
    assert 'char_003_ummi_layla' in line

def test_final_packaging_fails_closed_for_unapproved_episode():
    p=subprocess.run([sys.executable,'tools/package_episode.py','ep_tawakkul_lost_toy','--final'],cwd=ROOT,text=True,capture_output=True)
    assert p.returncode!=0
    assert 'FINAL PUBLICATION PACKAGE BLOCKED' in p.stdout+p.stderr

def test_master_prompt_matches_current_repo_version_when_supplied():
    p=ROOT/'MASTER_PROMPT.md'
    if not p.exists():
        return  # local-only artifact is intentionally absent from distribution
    text=p.read_text()
    m=re.search(r'\*\*Version:\*\*\s*([0-9.]+)',text)
    assert m and m.group(1)==current_version()
