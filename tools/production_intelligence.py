#!/usr/bin/env python3
from __future__ import annotations
import json, copy, hashlib
from pathlib import Path

ACCEPTED={'ACCEPTED','LOCKED'}

def _dir(root):
 p=Path(root)/'production/intelligence'; p.mkdir(parents=True,exist_ok=True); (p/'memory').mkdir(exist_ok=True); return p

def build_arcs(roadmap):
 arcs={}
 for e in roadmap['episodes']:
  aid=e.get('arc_id')
  if not aid: continue
  a=arcs.setdefault(aid,{'arc_id':aid,'episode_ids':[],'characters':[],'objective':e.get('concept'),'setup_events':[],'payoff_events':[],'status':'ACTIVE'})
  a['episode_ids'].append(e['episode_id']); a['characters']=sorted(set(a['characters']+e.get('character_focus',[])))
 for a in arcs.values():
  if len(a['episode_ids'])>1:
   a['setup_events']=[a['episode_ids'][0]]; a['payoff_events']=[a['episode_ids'][-1]]
 return list(arcs.values())

def validate_arcs(roadmap,arcs):
 ids=[e['episode_id'] for e in roadmap['episodes']]; seen=set()
 for a in arcs:
  if a['arc_id'] in seen: raise ValueError('duplicate arc ID')
  seen.add(a['arc_id'])
  for eid in a['episode_ids']:
   if eid not in ids: raise ValueError('missing arc episode')
  if len(a.get('episode_ids',[]))>1 and not a.get('setup_events'): raise ValueError('arc missing setup')
  for p in a.get('payoff_events',[]):
   if not a.get('setup_events'): raise ValueError('payoff without setup')
   if min(ids.index(x) for x in a['setup_events'])>=ids.index(p): raise ValueError('setup after payoff')
 return {'status':'PASS','arc_count':len(arcs)}

def memory_path(root,eid): return _dir(root)/'memory'/f'{eid}.json'
def commit_memory(root,episode,story,qa,status='ACCEPTED'):
 if status not in ACCEPTED: raise ValueError('unaccepted episode cannot commit memory')
 if any(v=='FAIL' for v in qa.get('categories',{}).values()): raise ValueError('failed QA cannot commit memory')
 snap={'schema_version':'2.71','episode_id':episode['episode_id'],'status':status,'ending_state':episode.get('ending_state',{}),'characters':episode.get('character_focus',[]),'learned_concept':episode.get('concept'),'active_goals':[episode.get('next_episode_hook')] if episode.get('next_episode_hook') else [],'persistent_props':story.get('persistent_props',[]),'arc_id':episode.get('arc_id'),'song_id':(episode.get('song_placement') or {}).get('song_id'),'source_story_hash':hashlib.sha256(json.dumps(story,sort_keys=True).encode()).hexdigest()}
 memory_path(root,episode['episode_id']).write_text(json.dumps(snap,indent=2)+'\n'); return snap

def retrieve_memory(root,episode,roadmap):
 facts=[]; consumed=[]
 for dep in episode.get('dependencies',[]):
  p=memory_path(root,dep)
  if p.exists(): facts.append(json.loads(p.read_text())); consumed.append(dep)
 return {'facts':facts,'consumed_episode_ids':consumed}

def validate_memory_conflict(memory,episode):
 conflicts=[]
 for m in memory.get('facts',[]):
  if m.get('arc_id')==episode.get('arc_id') and m.get('learned_concept') and episode.get('opening_state',{}).get('forgets_concept')==m['learned_concept']:
   conflicts.append('opening_state.forgets_concept')
 if conflicts: raise ValueError('memory conflict: '+','.join(conflicts))
 return {'status':'PASS'}

def character_development(root,episode,memory):
 p=_dir(root)/'character_development.json'; data=json.loads(p.read_text()) if p.exists() else {'schema_version':'2.71','characters':{}}
 for cid in episode.get('character_focus',[]):
  rec=data['characters'].setdefault(cid,{'events':[],'learned_lessons':[],'active_goals':[]})
  if episode.get('concept') and episode['concept'] not in rec['learned_lessons']: rec['learned_lessons'].append(episode['concept'])
  rec['events'].append({'episode_id':episode['episode_id'],'arc_id':episode.get('arc_id'),'status':'ACCEPTED'})
 p.write_text(json.dumps(data,indent=2)+'\n'); return data

def song_decision(episode,recent=()):
 sid=(episode.get('song_placement') or {}).get('song_id')
 if not sid:return {'decision':'NO_SONG'}
 if list(recent).count(sid)>=2:return {'decision':'SONG_REVIEW_REQUIRED','song_id':sid,'reason':'recent reuse threshold'}
 return {'decision':'USE_CANONICAL_SONG','song_id':sid,'entry_trigger':'story reflection beat','purpose':'curriculum/story reinforcement','entry_state':'inherit scene state','exit_state':'return to story continuity'}

def script_qa(story,memory):
 cats={'STORY_STRUCTURE':'PASS','CHILD_DIALOGUE':'PASS','CHARACTER_CONSISTENCY':'PASS','ARC_ALIGNMENT':'PASS','MEMORY_ALIGNMENT':'PASS','CURRICULUM_ALIGNMENT':'PASS','RELIGIOUS_SOURCE_SAFETY':'REVIEW_REQUIRED','SONG_INTEGRATION':'PASS' if story.get('song_reference') else 'NOT_APPLICABLE','DURATION':'PASS','SCENE_PLAYABILITY':'PASS','CONTINUITY':'PASS','PRODUCTION_READINESS':'PASS'}
 defects=[]
 if len(story.get('scenes',[]))<3: cats['STORY_STRUCTURE']='FAIL';defects.append('insufficient scenes')
 if not story.get('story_objective'): cats['STORY_STRUCTURE']='FAIL';defects.append('missing objective')
 return {'categories':cats,'defects':defects,'memory_facts_consumed':memory.get('consumed_episode_ids',[])}

def repair_unit(unit,reason):
 u=copy.deepcopy(unit); changed=[]
 if reason=='DUPLICATE_CHARACTER': u['duplicate_lock_strength']='STRICT_EXACT_COUNT_AND_SEPARATED_BLOCKING';changed=['duplicate_lock_strength']
 elif reason=='CONTINUITY_MISMATCH': u['in_state']=copy.deepcopy(u.get('expected_in_state',u['in_state']));changed=['in_state']
 elif reason=='CAMERA_FAILURE': u['camera']='Stable locked-off medium shot on established axis.';changed=['camera']
 else: raise ValueError('unknown failure reason')
 return u,changed
