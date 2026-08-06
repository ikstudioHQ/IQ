from pathlib import Path
import json,sys,tempfile,pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.episode_autopilot import generate,validate_package,episode
from tools.production_contracts import ContractError,load_character_master,validate_generation_unit

def test_four_vertical_slices_exist_and_pass():
 for eid in ('ep_001','ep_004','ep_005','ep_006'):
  q=json.loads((ROOT/'production/autopilot/archive_v268'/eid/'qa_report.json').read_text()); assert q['generation_units']>0 and q['max_unit_duration']<=10 and q['categories']['GEMINI']=='PASS'

def test_song_slice_uses_reference_not_lyrics_copy():
 s=json.loads((ROOT/'production/autopilot/archive_v268/ep_004/story_script.json').read_text())
 assert s['song_integration']['song_id']=='song_002'; assert 'lyrics' not in s['song_integration']

def test_prompt_contract_contains_required_hard_locks():
 p=next((ROOT/'production/autopilot/archive_v268/ep_001/gemini').glob('*.md')).read_text()
 for x in ('READY-TO-PASTE GEMINI PROMPT','EXACT CHARACTER COUNT','EXACT DIALOGUE/LYRICS','REFERENCE IMAGE LOCK','IN_STATE','OUT_STATE','CHARACTER DUPLICATION NEGATIVE LOCK'): assert x in p

def test_unknown_roadmap_fails_closed():
 with pytest.raises(ValueError): episode(ROOT,'ep_999')

def test_generation_unit_adversarial_timing_and_unknown_character():
 chars=load_character_master(ROOT); u={'generation_unit_id':'x','parent_scene_id':'s','start_seconds':0,'end_seconds':11,'visible_characters':['char_001_zayd'],'performance':[],'in_state':{},'out_state':{}}
 with pytest.raises(ContractError): validate_generation_unit(u,chars)
 u['end_seconds']=8;u['visible_characters']=['char_unknown']
 with pytest.raises(ContractError): validate_generation_unit(u,chars)

def test_deterministic_regeneration_hash():
 r=json.loads((ROOT/'production/roadmaps/active_roadmap.json').read_text()); eid=r['episodes'][0]['episode_id']; generate(ROOT,eid); q1=json.loads((ROOT/'production/autopilot/episodes'/eid/'production_manifest.json').read_text())['determinism_hash']; generate(ROOT,eid); q2=json.loads((ROOT/'production/autopilot/episodes'/eid/'production_manifest.json').read_text())['determinism_hash']; assert q1==q2
