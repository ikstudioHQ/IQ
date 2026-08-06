from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.authoring_pipeline import validate_authored_plan,render_gemini_prompt
from tools.production_contracts import load_character_master

def test_market_owner_is_canonical_and_scene4_authored():
 c=load_character_master(ROOT)['char_085_market_stall_owner']; assert c['approval_status']=='DRAFT' and c['approved_reference_image'] is None
 p=ROOT/'production/authored_generation_plans/episodes/ep_honesty_wallet_assisted/scene_4.json'; assert p.exists(); validate_authored_plan(ROOT,json.loads(p.read_text()))
 raw=(ROOT/'production/episodes/ep_honesty_wallet_assisted/scene_contract.json').read_text(); assert 'NONCANONICAL_BACKGROUND' not in raw

def test_existing_episode_coverage_10_of_10():
 scenes=sum(len(json.loads(p.read_text())['scenes']) for p in (ROOT/'production/episodes').glob('*/scene_contract.json'))
 authored=len(list((ROOT/'production/authored_generation_plans/episodes').glob('*/*.json'))); assert scenes==authored==10

def test_90_day_roadmap_complete_unique_and_connected():
 d=json.loads((ROOT/'production/roadmaps/archive/canonical_90_day_roadmap_v2.67_ARCHIVED.json').read_text()); eps=d['episodes']; assert len(eps)==90
 assert len({e['episode_id'] for e in eps})==90 and [e['day'] for e in eps]==list(range(1,91))
 topics={t['topic_id'] for t in json.loads((ROOT/'phase5/orchestration/planning/episode_topic_bank.json').read_text())['topics']}
 for i,e in enumerate(eps):
  assert e['topic_id'] in topics and e['curriculum_topic_reference'] in topics
  if i: assert eps[i-1]['episode_id'] in e['dependencies']
  assert e['script_status']=='AUTHORING_REQUIRED' and e['gemini_prompt_status']=='AUTHORING_REQUIRED'

def test_all_authored_prompts_duplication_and_duration_safe():
 for f in (ROOT/'production/authored_generation_plans').glob('*/*/*.json'):
  p=json.loads(f.read_text()); validate_authored_plan(ROOT,p)
  for u in p['generation_units']:
   assert u['end_seconds']-u['start_seconds']<=10
   text=render_gemini_prompt(ROOT,p,u); assert 'Exactly one instance of each listed character' in text and 'UNLISTED CHARACTER LOCK' in text
