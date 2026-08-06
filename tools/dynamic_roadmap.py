#!/usr/bin/env python3
"""v2.69 dynamic, versioned roadmap engine. Creative roadmap data is authored planning, never religious evidence."""
from __future__ import annotations
import argparse,json,hashlib,sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STATUS_LOCKED={'GENERATED','QA_REVIEWED','PUBLISHED','LOCKED'}
CAST=[['char_001_zayd','char_002_amira'],['char_002_amira','char_003_ummi_layla'],['char_001_zayd','char_004_baba_ahmad'],['char_001_zayd','char_002_amira','char_003_ummi_layla']]
LOC={'home':'home','school':'school','mosque':'mosque','park':'park','market':'market'}
def topic_bank(root=ROOT): return json.loads((root/'phase5/orchestration/planning/episode_topic_bank.json').read_text())['topics']
def songs(root=ROOT): return sorted(p.name for p in (root/'production/songs').glob('song_[0-9][0-9][0-9]') if p.is_dir())
def _title(t,n):
 base=t['working_title'].split('—',1)[0].strip(); return f"{base}: The Day {n} Choice"
def create(length:int,roadmap_id='roadmap_main',root=ROOT):
 if length<=0: raise ValueError('roadmap length must be positive')
 tb=topic_bank(root); sg=songs(root); eps=[]
 # Interleave topic bank rather than truncate legacy ordering.
 order=[(i*7)%len(tb) for i in range(length)] if length<=len(tb) else [i%len(tb) for i in range(length)]
 for pos,ti in enumerate(order,1):
  t=tb[ti]; eid=f'rm_{hashlib.sha1((roadmap_id+str(pos)+t["topic_id"]).encode()).hexdigest()[:10]}'
  setting=t.get('setting') or 'home'; song=None
  if pos in {4,11,18,25} and sg: song={'song_id':sg[(pos//7)%len(sg)],'policy':'canonical reference only; episode staging authored later'}
  eps.append({'order':pos,'episode_id':eid,'title':_title(t,pos),'topic_id':t['topic_id'],'curriculum_topic_reference':t['topic_id'],'concept':t['primary_concept'],'evidence_ids':t.get('evidence_ids',[]),'source_review_state':'INHERIT_EXISTING_EVIDENCE_REVIEW_STATE','story_premise':f"A child-scale {setting} choice makes {t['learning_objective'].rstrip('.').lower()} visible through consequence and repair.",'story_objective':t['learning_objective'],'character_focus':CAST[(pos-1)%len(CAST)],'locations':[setting],'conflict_id':t.get('conflict_id'),'arc_id':f'arc_{(pos-1)//3+1:02d}' if pos%5 else f'arc_single_{pos:03d}','dependencies':[] if pos==1 else [eps[-1]['episode_id']],'opening_state':{'inherits_from':None if pos==1 else eps[-1]['episode_id']+'.ending_state'},'ending_state':{'lesson_progress':t['primary_concept'],'memory_note':'Persist only accepted consequences/relationship changes after production review.'},'next_episode_hook':'Continue accepted state into next episode.' if pos<length else 'Season ending; future extension may begin from accepted snapshot.','song_placement':song,'status':'ROADMAP_DRAFT','production_status':'NOT_STARTED','review_status':'REVIEW_REQUIRED'})
 return {'schema_version':'2.69','roadmap_id':roadmap_id,'roadmap_version':1,'requested_episode_count':length,'status':'ROADMAP_DRAFT','provenance_class':'AUTHORED_CREATIVE_STORY_PLAN','episodes':eps,'history':[{'version':1,'action':'created','episode_count':length}]}
def validate(r):
 eps=r['episodes']; exp=r['requested_episode_count']
 if exp<=0 or len(eps)!=exp: raise ValueError('roadmap episode count mismatch')
 ids=[e['episode_id'] for e in eps]
 if len(ids)!=len(set(ids)): raise ValueError('duplicate episode ID')
 m=set(ids)
 for i,e in enumerate(eps,1):
  if e['order']!=i: raise ValueError('invalid roadmap order')
  if not e.get('curriculum_topic_reference'): raise ValueError('missing curriculum/topic reference')
  for d in e.get('dependencies',[]):
   if d not in m: raise ValueError('broken dependency')
   if ids.index(d)>=ids.index(e['episode_id']): raise ValueError('dependency cycle/forward dependency')
 return {'status':'PASS','episode_count':len(eps),'dependency_errors':0}
def revise(r,action,**kw):
 r=copy.deepcopy(r); validate(r); r['roadmap_version']+=1
 if action=='extend':
  n=int(kw['length']);
  if n<len(r['episodes']): raise ValueError('extension must increase length')
  fresh=create(n,r['roadmap_id']); fresh['episodes'][:len(r['episodes'])]=r['episodes']; r['episodes']=fresh['episodes']; r['requested_episode_count']=n
 elif action=='shorten':
  n=int(kw['length']);
  if n<=0 or n>=len(r['episodes']): raise ValueError('invalid shortening')
  if any(e['status'] in STATUS_LOCKED for e in r['episodes'][n:]): raise ValueError('cannot delete produced/locked episode')
  r['episodes']=r['episodes'][:n];r['requested_episode_count']=n;r['episodes'][-1]['next_hook']='Season ending after controlled shortening.'
 elif action=='lock': r['status']='ROADMAP_APPROVED'; [e.update(status='LOCKED') for e in r['episodes']]
 else: raise ValueError('unsupported revision action')
 r.setdefault('history',[]).append({'version':r['roadmap_version'],'action':action,'episode_count':len(r['episodes'])}); validate(r); return r
def impact(r,eid):
 ids=[e['episode_id'] for e in r['episodes']];
 if eid not in ids: raise ValueError('missing episode')
 deps=[e['episode_id'] for e in r['episodes'] if eid in e.get('dependencies',[])]
 e=next(e for e in r['episodes'] if e['episode_id']==eid)
 return {'episode_id':eid,'direct_dependents':deps,'locked_content_at_risk':e['status'] in STATUS_LOCKED,'affected_arc':e['arc_id'],'affected_song':(e.get('song_placement') or {}).get('song_id')}
def edit_future(r, action, episode_id=None, position=None, replacement=None):
 r=copy.deepcopy(r); validate(r); ids=[e["episode_id"] for e in r["episodes"]]
 if episode_id and episode_id not in ids: raise ValueError("missing episode")
 if episode_id:
  idx=ids.index(episode_id); old=r["episodes"][idx]
  if old["status"] in STATUS_LOCKED: raise ValueError("locked episode requires controlled revision")
 if action=="replace":
  if not replacement: raise ValueError("replacement required")
  replacement=copy.deepcopy(replacement); replacement["episode_id"]=old["episode_id"]; replacement["order"]=old["order"]; r["episodes"][idx]=replacement
 elif action=="reorder":
  if position is None or position<1 or position>len(r["episodes"]): raise ValueError("invalid reorder position")
  item=r["episodes"].pop(idx); r["episodes"].insert(position-1,item)
 elif action=="insert":
  if position is None or position<1 or position>len(r["episodes"])+1 or not replacement: raise ValueError("invalid insert")
  item=copy.deepcopy(replacement);
  if item["episode_id"] in ids: raise ValueError("duplicate episode ID")
  r["episodes"].insert(position-1,item);r["requested_episode_count"]+=1
 else: raise ValueError("unsupported edit action")
 for i,e in enumerate(r["episodes"],1): e["order"]=i
 # Rebuild simple serial dependencies for mutable roadmap structure.
 for i,e in enumerate(r["episodes"]): e["dependencies"]=[] if i==0 else [r["episodes"][i-1]["episode_id"]]
 r["roadmap_version"]+=1;r.setdefault("history",[]).append({"version":r["roadmap_version"],"action":action,"episode_count":len(r["episodes"])})
 validate(r);return r

def preview(r):
 return '\n'.join(f"Day {e['order']:02d} | {e['episode_id']} | {e['title']} | {', '.join(e['character_focus'])} | {e['concept']} | {e['arc_id']} | song={(e.get('song_placement') or {}).get('song_id','-')} | prev={(e.get('dependencies') or ['-'])[0]} | {e['review_status']}" for e in r['episodes'])
def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest='cmd',required=True)
 c=sp.add_parser('create');c.add_argument('length',type=int);c.add_argument('--id',default='roadmap_main');c.add_argument('--out',required=True)
 v=sp.add_parser('validate');v.add_argument('file');p=sp.add_parser('preview');p.add_argument('file')
 x=ap.parse_args()
 if x.cmd=='create':
  r=create(x.length,x.id);Path(x.out).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(validate(r)))
 else:
  r=json.loads(Path(x.file).read_text());print(json.dumps(validate(r)) if x.cmd=='validate' else preview(r))
if __name__=='__main__': main()
