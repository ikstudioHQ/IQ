from pathlib import Path
import sys,json,pytest,copy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.production_intelligence import *
from tools.episode_autopilot import generate
from tools.dynamic_roadmap import validate

def active(): return json.loads((ROOT/'production/roadmaps/active_roadmap.json').read_text())
def test_arcs_operational():
 r=active(); a=build_arcs(r); assert validate_arcs(r,a)['arc_count']>0
 bad=copy.deepcopy(a); multi=next(x for x in bad if len(x['episode_ids'])>1);multi['setup_events']=[]
 with pytest.raises(ValueError): validate_arcs(r,bad)
def test_memory_commit_policy_and_retrieval(tmp_path):
 r=active();a,b=r['episodes'][:2];story={'persistent_props':[]};qa={'categories':{'STORY':'PASS'}}
 with pytest.raises(ValueError):commit_memory(tmp_path,a,story,qa,'GENERATED')
 commit_memory(tmp_path,a,story,qa,'ACCEPTED');m=retrieve_memory(tmp_path,b,r);assert m['consumed_episode_ids']==[a['episode_id']]
def test_memory_conflict():
 e={'arc_id':'x','opening_state':{'forgets_concept':'honesty'}};m={'facts':[{'arc_id':'x','learned_concept':'honesty'}]}
 with pytest.raises(ValueError):validate_memory_conflict(m,e)
def test_song_planner():
 assert song_decision({})['decision']=='NO_SONG'; assert song_decision({'song_placement':{'song_id':'song_001'}})['decision']=='USE_CANONICAL_SONG'
 assert song_decision({'song_placement':{'song_id':'song_001'}},['song_001','song_001'])['decision']=='SONG_REVIEW_REQUIRED'
def test_retry_is_local():
 u={'generation_unit_id':'u1','in_state':{},'camera':'x'};v,ch=repair_unit(u,'DUPLICATE_CHARACTER');assert ch==['duplicate_lock_strength'] and u.get('duplicate_lock_strength') is None
def test_autopilot_consumes_memory(tmp_path):
 r=active();a,b=r['episodes'][:2]; qa=generate(ROOT,a['episode_id'],outbase=tmp_path/'a'); assert qa['max_unit_duration']<=10
 # root memory intentionally not committed by draft generation
 q2=generate(ROOT,b['episode_id'],outbase=tmp_path/'b'); story=json.loads((tmp_path/'b/story_script.json').read_text()); assert story['memory_context']['consumed_episode_ids'] in ([],[a['episode_id']])
def test_active_roadmap_still_valid(): assert validate(active())['episode_count']==30
