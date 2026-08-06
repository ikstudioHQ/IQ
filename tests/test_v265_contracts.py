import json, shutil
from pathlib import Path
import pytest
from tools.preflight_check import run
from tools.production_contracts import *
ROOT=Path(__file__).resolve().parents[1]

def test_distribution_master_absent_is_valid():
    assert not (ROOT/'MASTER_PROMPT.md').exists()
    assert run(str(ROOT), profile='distribution')[0]=='REPOSITORY_VERIFIED'

def test_local_master_absent_blocks():
    assert run(str(ROOT), profile='local')[0]=='REPOSITORY_INCOMPLETE'

def test_local_master_version_profiles(tmp_path):
    for name in ('knowledge_index.json','repository_manifest.json','VERSION_COMPATIBILITY.md','DESIGN_PRINCIPLES.md','AUTHORITY_HIERARCHY.md'):
        shutil.copy(ROOT/name,tmp_path/name)
    for d in ('phase2/data/islamic','sources/characters/characters','phase1/docs/governance','phase2/data/config'):
        (tmp_path/d).mkdir(parents=True)
        for f in (ROOT/d).glob('*'):
            if f.is_file(): shutil.copy(f,tmp_path/d/f.name)
    (tmp_path/'MASTER_PROMPT.md').write_text('Repository Version: **v2.72**')
    assert run(str(tmp_path),profile='local')[0]=='REPOSITORY_VERIFIED'
    (tmp_path/'MASTER_PROMPT.md').write_text('Repository Version: **v9.99**')
    assert run(str(tmp_path),profile='local')[0]=='REPOSITORY_VERSION_MISMATCH'

def test_active_legacy_ids_removed():
    for rel in ['phase2/data/database','phase3/knowledge/characters']:
        for p in (ROOT/rel).glob('*.json'):
            t=p.read_text()
            assert '"char_zayd"' not in t and '"char_amira"' not in t

def test_character_and_performance_adversarial():
    chars=load_character_master(ROOT); z='char_001_zayd'; a='char_002_amira'
    with pytest.raises(ContractError): validate_character_ref('char_zayd',chars)
    base={'generation_unit_id':'u1','parent_scene_id':'s1','start_seconds':0,'end_seconds':8,'visible_characters':[z], 'performance':[], 'in_state':{},'out_state':{}}
    validate_generation_unit(base,chars)
    bad=dict(base,visible_characters=[z],performance=[{'character_id':a,'type':'dialogue','text':'x'}])
    with pytest.raises(ContractError): validate_generation_unit(bad,chars)
    bad=dict(base,performance=[{'character_id':z,'type':'silent','text':'x','lip_sync':True}])
    with pytest.raises(ContractError): validate_generation_unit(bad,chars)
    bad=dict(base,end_seconds=11)
    with pytest.raises(ContractError): validate_generation_unit(bad,chars)

def test_continuity_and_long_scene_fail_closed():
    with pytest.raises(ContractError): validate_continuity({'location':'a'},{'location':'b'})
    validate_continuity({'location':'a'},{'location':'b','transition_from_previous':['location']})
    with pytest.raises(ContractError,match='AUTHORING_REQUIRED'): require_generation_units_for_scene({'duration_seconds':40})

def test_canonical_song_reference():
    validate_song_reference(ROOT,'song_001')
    with pytest.raises(ContractError): validate_song_reference(ROOT,'song_999')

from tools.authoring_pipeline import validate_authored_plan, render_gemini_prompt, compile_plan

def test_authored_song_vertical_slice(tmp_path):
    p=ROOT/'tests/fixtures/v265_authoring/song_001_scene_02_authored.json'; plan=json.loads(p.read_text())
    assert validate_authored_plan(ROOT,plan)
    m=compile_plan(ROOT,p,tmp_path/'song'); assert m['generation_ready'] and len(m['units'])==2
    text=(tmp_path/'song/song_001_scene_02_u01.md').read_text()
    assert 'EXACT CHARACTER COUNT: 3' in text and 'No clones, twins, duplicate bodies' in text and 'Do not add any character' in text

def test_authored_episode_vertical_slice(tmp_path):
    p=ROOT/'tests/fixtures/v265_authoring/episode_tawakkul_scene_01_authored.json'; plan=json.loads(p.read_text())
    assert validate_authored_plan(ROOT,plan)
    m=compile_plan(ROOT,p,tmp_path/'episode'); assert len(m['units'])==2

def test_authoring_required_and_duplicate_resistance():
    chars=load_character_master(ROOT); z='char_001_zayd'
    with pytest.raises(ContractError,match='AUTHORING_REQUIRED'): validate_authored_plan(ROOT,{'provenance_class':'AUTHORED_PRODUCTION_DIRECTION','parent_type':'episode','parent_id':'x','generation_units':[]})
    base={'generation_unit_id':'u','parent_scene_id':'s','start_seconds':0,'end_seconds':5,'exact_character_count':2,'visible_characters':[z,z],'performance':[],'in_state':{},'out_state':{}}
    plan={'provenance_class':'AUTHORED_PRODUCTION_DIRECTION','parent_type':'episode','parent_id':'x','generation_units':[base]}
    with pytest.raises(ContractError,match='duplicate physical'): validate_authored_plan(ROOT,plan)

def test_authored_timing_impossible_blocks():
    z='char_001_zayd'; u={'generation_unit_id':'u','parent_scene_id':'s','start_seconds':0,'end_seconds':2,'exact_character_count':1,'visible_characters':[z],'performance':[{'character_id':z,'type':'dialogue','text':'one two three four five six seven eight nine ten','start_seconds':0,'end_seconds':2}], 'in_state':{},'out_state':{}}
    p={'provenance_class':'AUTHORED_PRODUCTION_DIRECTION','parent_type':'episode','parent_id':'x','generation_units':[u]}
    with pytest.raises(ContractError,match='AUTHORING_REQUIRED'): validate_authored_plan(ROOT,p)
