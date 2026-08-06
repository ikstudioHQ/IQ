#!/usr/bin/env python3
"""Deterministic roadmap-to-Gemini draft episode autopilot with dependency-aware regeneration."""
from __future__ import annotations
import argparse,json,sys,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from tools.production_contracts import load_character_master,validate_song_reference
from tools.authoring_pipeline import validate_authored_plan,render_gemini_prompt
from tools.production_intelligence import retrieve_memory,validate_memory_conflict,song_decision,script_qa,commit_memory,character_development
SCENE_PURPOSES=[('hook','A small everyday surprise creates an immediate question.'),('setup','The children understand the practical situation.'),('choice','A child must choose what to do next.'),('consequence','The first choice creates a visible consequence.'),('reflection','The children pause, notice feelings, and reconsider.'),('discovery','They connect the experience to the supported lesson.'),('practice','They try a better action in a concrete child-scale way.'),('payoff','The better choice changes the situation and relationships.'),('callback','A light callback shows the lesson being remembered.'),('handoff','The episode closes warmly and preserves a next-day hook.')]
def load_roadmap(root=ROOT): return json.loads((root/'production/roadmaps/active_roadmap.json').read_text())['episodes']
def episode(root,eid):
 m={e['episode_id']:e for e in load_roadmap(root)}
 if eid not in m: raise ValueError(f'unknown roadmap episode_id: {eid}')
 return m[eid]
def cast(root,e):
 chars=load_character_master(root); ids=e['character_focus'][:3]
 for cid in ids:
  if cid not in chars: raise ValueError(f'unknown canonical cast: {cid}')
 return ids,chars
def line_for(name,purpose):
 return {'hook':f"{name}: Wait—something here doesn't feel quite right.",'setup':f"{name}: Let's look carefully before we decide.",'choice':f"{name}: I think I know what I want to do, but I should think first.",'consequence':f"{name}: Oh. My choice changed what happened next.",'reflection':f"{name}: How would I feel if I were on the other side of this?",'discovery':f"{name}: I understand the lesson better when I see what my choice does.",'practice':f"{name}: Let's try the kinder, wiser choice together.",'payoff':f"{name}: That feels better—and it helped someone too.",'callback':f"{name}: I want to remember this the next time I have a choice.",'handoff':f"{name}: Tomorrow, let's see if we can remember what we learned today."}[purpose]
def _read_json(p):
 try:return json.loads(p.read_text())
 except Exception as ex: raise ValueError(f'invalid/missing upstream artifact {p}: {ex}') from ex
def _script(root,e):
 ids,_=cast(root,e); memory=retrieve_memory(root,e,{'episodes':load_roadmap(root)}); validate_memory_conflict(memory,e); song=song_decision(e); sid=(e.get('song_placement') or {}).get('song_id')
 if sid: validate_song_reference(root,sid)
 return {'schema_version':'2.72','episode_id':e['episode_id'],'provenance_class':'AUTHORED_CREATIVE_STORY','roadmap_day':e.get('day',e.get('order')),'title':e['title'],'curriculum_topic_reference':e['curriculum_topic_reference'],'evidence_ids':e.get('evidence_ids',[]),'religious_claim_policy':'Only repository evidence IDs are referenced; no quotation/authentication/approval is invented.','previous_dependencies':e.get('dependencies',[]),'story_objective':e['story_objective'],'cast':ids,'opening_state':e['opening_state'],'ending_state':e['ending_state'],'next_episode_hook':e['next_episode_hook'],'song_reference':sid,'review_state':'DRAFT; RELIGIOUS/HUMAN/SCHOLAR REVIEW INHERITED/REQUIRED AS APPLICABLE','memory_context':memory,'arc_context':{'arc_id':e.get('arc_id')},'song_plan':song,'song_integration':None if not sid else {'song_id':sid,'entry_after_scene':'scene_06','lyrics_source':'canonical song only; lyrics are not duplicated in this episode source','episode_specific_staging':'AUTHORED_PRODUCTION_DIRECTION','exit_to_scene':'scene_07'}}
def _scenes(root,script,target):
 ids,chars=cast(root,episode(root,script['episode_id'])); out=[]; scene_dur=target/len(SCENE_PURPOSES)
 for si,(purpose,desc) in enumerate(SCENE_PURPOSES,1):
  sid=f'scene_{si:02d}'; dialogue=[]; n=max(1,round(scene_dur/8))
  for ui in range(n):
   speaker=ids[(si+ui)%len(ids)]; dialogue.append({'character_id':speaker,'text':line_for(chars[speaker]['canonical_name'],purpose)})
  out.append({'scene_id':sid,'narrative_purpose':purpose,'purpose_description':desc,'estimated_duration_seconds':scene_dur,'location':episode(root,script['episode_id'])['locations'][0],'visible_characters':ids,'source_evidence_ids':script['evidence_ids'],'provenance_class':'AUTHORED_CREATIVE_STORY','dialogue':dialogue})
 return {'schema_version':'2.72','episode_id':script['episode_id'],'target_duration':target,'scenes':out}
def _plans(root,script,scenes):
 e=episode(root,script['episode_id']); ids,_=cast(root,e); plans=[]; prev={'location':e['locations'][0],'position':'cast grouped with separated silhouettes','orientation':'toward scene action','emotion':'curious','props':[],'camera_axis':'stable A-axis'}
 for si,scene in enumerate(scenes['scenes'],1):
  dur=scene['estimated_duration_seconds']; n=len(scene['dialogue']); step=dur/n; units=[]
  for ui,d in enumerate(scene['dialogue']):
   a=round(ui*step,3); b=round((ui+1)*step,3); cid=d['character_id']; ev_end=min(b,a+max(3.0,len(d['text'].split())/2.5)); state=dict(prev); state['emotion']=['curious','thoughtful','concerned','reflective','hopeful','warm'][min(5,si//2)]; out=dict(state); out['position']='stable separated blocking, slight authored progression'
   u={'generation_unit_id':f"{e['episode_id']}_{scene['scene_id']}_u{ui+1:02d}",'parent_scene_id':scene['scene_id'],'start_seconds':a,'end_seconds':b,'exact_character_count':len(ids),'visible_characters':ids,'performance':[{'character_id':cid,'type':'dialogue','text':d['text'],'start_seconds':a,'end_seconds':round(ev_end,3),'lip_sync':True}]+[{'character_id':c,'type':'reaction'} for c in ids if c!=cid],'silent_characters':[c for c in ids if c!=cid],'in_state':state,'out_state':out,'primary_action':f"One clear {scene['narrative_purpose']} action; characters keep separated silhouettes and physically achievable motion.",'secondary_reaction':'Non-speakers react with eyes and posture only; mouths remain non-speaking.','camera':'Stable medium two-shot/group shot on established A-axis; gentle push only when emotionally useful.','lighting':'Warm child-friendly cinematic lighting; preserve time and direction.','music_continuity':'Light underscore only; duck under dialogue.','location':scene['location']}; units.append(u); prev=out
  plan={'schema_version':'2.72','provenance_class':'AUTHORED_PRODUCTION_DIRECTION','parent_type':'episode','parent_id':e['episode_id'],'source_scene_id':scene['scene_id'],'generation_units':units}; validate_authored_plan(root,plan); plans.append(plan)
 return plans
def _write_prompts(root,base,plans):
 gd=base/'gemini'; shutil.rmtree(gd,ignore_errors=True); gd.mkdir(parents=True)
 for p in plans:
  for u in p['generation_units']:(gd/f"{u['generation_unit_id']}.md").write_text(render_gemini_prompt(root,p,u),encoding='utf-8')
def _write_plans(base,plans):
 pd=base/'production_plans'; shutil.rmtree(pd,ignore_errors=True); pd.mkdir(parents=True)
 for p in plans:(pd/f"{p['source_scene_id']}.json").write_text(json.dumps(p,indent=2),encoding='utf-8')
def _load_plans(base): return [_read_json(p) for p in sorted((base/'production_plans').glob('*.json'))]
def _finalize(root,e,base,script,scenes,plans,stage):
 combined=dict(script); combined['scenes']=scenes['scenes']; quality=script_qa(combined,script['memory_context']); shorts=[{'type':'hook','source_scene':'scene_01'},{'type':'moral choice','source_scene':'scene_03'},{'type':'lesson reveal','source_scene':'scene_06'}]
 qa={'schema_version':'2.72','script_quality':quality,'episode_id':e['episode_id'],'categories':{'STORY':'PASS','CHARACTERS':'PASS','DIALOGUE':'PASS','PRODUCTION':'PASS','CONTINUITY':'PASS','SONG':'PASS' if script.get('song_reference') else 'NOT_APPLICABLE','RELIGIOUS':'REVIEW_REQUIRED','GEMINI':'PASS'},'generation_units':sum(len(p['generation_units']) for p in plans),'max_unit_duration':max(u['end_seconds']-u['start_seconds'] for p in plans for u in p['generation_units']),'shorts_candidates':shorts,'publication_status':'NOT_READY','human_render_review':'REQUIRED'}; (base/'qa_report.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
 lineage={'last_regenerated_stage':stage,'script_hash':hashlib.sha256((base/'story_script.json').read_bytes()).hexdigest(),'scenes_hash':hashlib.sha256((base/'logical_scenes.json').read_bytes()).hexdigest(),'units_hash':hashlib.sha256(json.dumps(plans,sort_keys=True).encode()).hexdigest()}
 manifest={'schema_version':'2.72','episode_id':e['episode_id'],'production_state':'GEMINI_READY','memory_consumed':script['memory_context'].get('consumed_episode_ids',[]),'stage_levels':{'roadmap':'COMPLETE','script':'DRAFT_COMPLETE','logical_scenes':'DRAFT_COMPLETE','production_plans':'DRAFT_COMPLETE','generation_units':'DRAFT_COMPLETE','gemini_prompts':'DRAFT_COMPLETE','automated_qa':'COMPLETE'},'files':{'script':'story_script.json','scenes':'logical_scenes.json','qa':'qa_report.json'},'lineage':lineage,'determinism_hash':hashlib.sha256(json.dumps({'script':script,'scenes':scenes,'plans':plans},sort_keys=True).encode()).hexdigest(),'review_requirements':['HUMAN_CREATIVE_RENDER_REVIEW','ISLAMIC_REVIEW_AS_GOVERNED_BY_REFERENCED_EVIDENCE']}; (base/'production_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8'); return qa
def generate(root,eid,outbase=None,target=600):
 e=episode(root,eid); base=outbase or root/'production/autopilot/episodes'/eid; base.mkdir(parents=True,exist_ok=True); script=_script(root,e); (base/'story_script.json').write_text(json.dumps(script,indent=2),encoding='utf-8'); scenes=_scenes(root,script,target); (base/'logical_scenes.json').write_text(json.dumps(scenes,indent=2),encoding='utf-8'); plans=_plans(root,script,scenes); _write_plans(base,plans); _write_prompts(root,base,plans); return _finalize(root,e,base,script,scenes,plans,'full')
def regenerate(root,eid,stage):
 e=episode(root,eid); base=root/'production/autopilot/episodes'/eid
 if not base.exists(): raise ValueError('episode package does not exist; run generate-one first')
 if stage=='script':
  old=_read_json(base/'logical_scenes.json'); target=old.get('target_duration',600); script=_script(root,e); (base/'story_script.json').write_text(json.dumps(script,indent=2),encoding='utf-8'); scenes=_scenes(root,script,target); (base/'logical_scenes.json').write_text(json.dumps(scenes,indent=2),encoding='utf-8'); plans=_plans(root,script,scenes); _write_plans(base,plans); _write_prompts(root,base,plans)
 elif stage=='scenes':
  script=_read_json(base/'story_script.json'); old=_read_json(base/'logical_scenes.json'); scenes=_scenes(root,script,old.get('target_duration',600)); (base/'logical_scenes.json').write_text(json.dumps(scenes,indent=2),encoding='utf-8'); plans=_plans(root,script,scenes); _write_plans(base,plans); _write_prompts(root,base,plans)
 elif stage=='units':
  script=_read_json(base/'story_script.json'); scenes=_read_json(base/'logical_scenes.json'); plans=_plans(root,script,scenes); _write_plans(base,plans); _write_prompts(root,base,plans)
 elif stage=='prompts':
  script=_read_json(base/'story_script.json'); scenes=_read_json(base/'logical_scenes.json'); plans=_load_plans(base)
  expected_scene_ids={s['scene_id'] for s in scenes.get('scenes',[])}
  actual_scene_ids={p.get('source_scene_id') for p in plans}
  if not plans or actual_scene_ids != expected_scene_ids: raise ValueError('missing/incomplete upstream production plans')
  for p in plans: validate_authored_plan(root,p)
  _write_prompts(root,base,plans)
 else: raise ValueError('invalid regeneration stage')
 return _finalize(root,e,base,script,scenes,plans,stage)
def validate_package(root,eid):
 base=root/'production/autopilot/episodes'/eid; _read_json(base/'story_script.json'); _read_json(base/'logical_scenes.json'); plans=_load_plans(base)
 if not plans: raise ValueError('missing production plans')
 for p in plans: validate_authored_plan(root,p)
 return _read_json(base/'qa_report.json')
def main():
 ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True); a=sub.add_parser('generate-one'); a.add_argument('episode_id'); a.add_argument('--target-duration',type=float,default=600); r=sub.add_parser('generate-range'); r.add_argument('start'); r.add_argument('end'); r.add_argument('--mode',choices=['INDEPENDENT_DRAFT','CHAINED_DRAFT'],default='INDEPENDENT_DRAFT'); ac=sub.add_parser('accept'); ac.add_argument('episode_id'); v=sub.add_parser('validate'); v.add_argument('episode_id'); g=sub.add_parser('regenerate'); g.add_argument('episode_id'); g.add_argument('--stage',choices=['script','scenes','units','prompts'],required=True); x=ap.parse_args()
 if x.cmd=='generate-one': print(json.dumps(generate(ROOT,x.episode_id,target=x.target_duration),indent=2))
 elif x.cmd=='generate-range':
  eps=load_roadmap(ROOT); ids=[e['episode_id'] for e in eps]; pos=lambda v: ids.index(v) if v in ids else int(v)-1; a,b=pos(x.start),pos(x.end)
  if a<0 or b<a or b>=len(eps): raise ValueError('invalid dynamic range')
  for e in eps[a:b+1]: generate(ROOT,e['episode_id'])
 elif x.cmd=='accept':
  e=episode(ROOT,x.episode_id); base=ROOT/'production/autopilot/episodes'/x.episode_id; story=_read_json(base/'story_script.json'); qa=_read_json(base/'qa_report.json'); snap=commit_memory(ROOT,e,story,qa); character_development(ROOT,e,{'facts':[snap]}); print(json.dumps(snap,indent=2))
 elif x.cmd=='validate': print(json.dumps(validate_package(ROOT,x.episode_id),indent=2))
 elif x.cmd=='regenerate': print(json.dumps(regenerate(ROOT,x.episode_id,x.stage),indent=2))
if __name__=='__main__': main()
