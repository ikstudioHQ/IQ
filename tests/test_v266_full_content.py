from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from tools.authoring_pipeline import validate_authored_plan,render_gemini_prompt
from tools.production_contracts import ContractError,load_character_master

def plans(): return sorted((ROOT/'production/authored_generation_plans').rglob('scene_*.json'))

def test_all_100_song_scenes_authored_and_valid():
    fs=list((ROOT/'production/authored_generation_plans/songs').rglob('scene_*.json')); assert len(fs)==100
    for f in fs: validate_authored_plan(ROOT,json.loads(f.read_text()))

def test_episode_authored_coverage_completed_in_v267():
    contracts=[]
    for p in (ROOT/'production/episodes').glob('*/scene_contract.json'): contracts.extend(json.loads(p.read_text())['scenes'])
    authored=list((ROOT/'production/authored_generation_plans/episodes').rglob('scene_*.json'))
    assert len(contracts)==10 and len(authored)==10
    raw=(ROOT/'production/episodes/ep_honesty_wallet_assisted/scene_contract.json').read_text()
    assert 'char_085_market_stall_owner' in raw

def test_all_authored_units_max_10_and_duplication_safe():
    for f in plans():
        p=json.loads(f.read_text()); validate_authored_plan(ROOT,p)
        for u in p['generation_units']:
            assert u['end_seconds']-u['start_seconds']<=10
            assert len(u['visible_characters'])==len(set(u['visible_characters']))==u['exact_character_count']

def test_prompt_has_self_contained_duplicate_locks():
    p=json.loads(plans()[0].read_text()); text=render_gemini_prompt(ROOT,p,p['generation_units'][0])
    for needle in ['EXACT CHARACTER COUNT','Exactly one instance of each listed character','UNLISTED CHARACTER LOCK','INITIAL FRAME','IN_STATE','OUT_STATE','FINAL FRAME','CHARACTER DUPLICATION NEGATIVE LOCK']:
        assert needle in text

def test_song_episode_integration_references_only_canonical_song():
    d=json.loads((ROOT/'production/integrations/ep_tawakkul_song_001_demo.json').read_text())
    assert d['canonical_song_id']=='song_001' and d['canonical_lyrics_policy']=='REFERENCE_ONLY_NO_DUPLICATION'
    assert 'lyrics' not in d

def test_shorts_are_derived_pointers_only():
    d=json.loads((ROOT/'production/derived/shorts_candidates.json').read_text())
    assert d['provenance_class']=='DERIVED_OUTPUT_INDEX'
    assert all('source_id' in x and 'lyrics' not in x and 'dialogue' not in x for x in d['candidates'])

def test_adversarial_duplicate_unknown_and_timing_fail_closed():
    base=json.loads(plans()[0].read_text()); u=dict(base['generation_units'][0])
    u['visible_characters']=u['visible_characters']+[u['visible_characters'][0]]; u['exact_character_count']=len(u['visible_characters'])
    bad=dict(base); bad['generation_units']=[u]
    try: validate_authored_plan(ROOT,bad); assert False
    except ContractError: pass
    u=dict(base['generation_units'][0]); u['end_seconds']=u['start_seconds']+10.1; bad=dict(base); bad['generation_units']=[u]
    try: validate_authored_plan(ROOT,bad); assert False
    except ContractError: pass
