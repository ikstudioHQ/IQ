import copy, hashlib, importlib.util, json, shutil
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
def load(rel,name):
 spec=importlib.util.spec_from_file_location(name,ROOT/rel); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def test_foundational_duplicate_visible_characters_rejected():
 m=load('tools/production_contracts.py','pc272'); chars=m.load_character_master(ROOT); ids=list(chars)[:2]
 u={'generation_unit_id':'u','parent_scene_id':'s','start_seconds':0,'end_seconds':5,'visible_characters':[ids[0],ids[0]],'performance':[{'character_id':ids[0],'type':'reaction'}],'in_state':{},'out_state':{}}
 with pytest.raises(m.ContractError,match='duplicate visible'):m.validate_generation_unit(u,chars)
 u['visible_characters']=ids; assert m.validate_generation_unit(u,chars)
def test_release_hygiene_rejects_git():
 m=load('tools/release_hygiene.py','rh272'); assert m.is_prohibited(Path('.git/config'))
def test_final_religious_gate_direct_no_exception(tmp_path,monkeypatch):
 m=load('tools/package_episode.py','pe272'); monkeypatch.chdir(tmp_path); d=tmp_path/'output_package'/'ep'; d.mkdir(parents=True); (d/'verification_report.md').write_text('Evidence: ev1\n')
 monkeypatch.setattr(m,'islamic_entries_by_id',lambda:{'ev1':{'citation_verified':False,'source_verified':False,'scholarly_reviewed':False}})
 ok,problems=m.final_religious_gate('ep'); assert not ok and problems
 monkeypatch.setattr(m,'islamic_entries_by_id',lambda:{'ev1':{'citation_verified':True,'source_verified':True,'scholarly_reviewed':True}})
 ok,problems=m.final_religious_gate('ep'); assert ok and not problems
 (d/'verification_report.md').write_text('Evidence: unknown\n'); ok,problems=m.final_religious_gate('ep'); assert not ok and 'does not resolve' in problems[0]
def test_stage_regeneration_dependency_hashes(tmp_path):
 m=load('tools/episode_autopilot.py','ea272'); root=tmp_path/'repo'; shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','__pycache__','.pytest_cache'))
 eid=json.loads((root/'production/roadmaps/active_roadmap.json').read_text())['episodes'][0]['episode_id']; m.generate(root,eid); b=root/'production/autopilot/episodes'/eid
 script=b/'story_script.json'; scenes=b/'logical_scenes.json'; plan=sorted((b/'production_plans').glob('*.json'))[0]; prompt=sorted((b/'gemini').glob('*.md'))[0]
 base=(h(script),h(scenes),h(plan),h(prompt)); memdir=root/'production/intelligence/accepted_memory'; mem_before={p.name:h(p) for p in memdir.glob('*.json')} if memdir.exists() else {}
 prompt.write_text('CORRUPT'); m.regenerate(root,eid,'prompts'); assert (h(script),h(scenes),h(plan))==base[:3] and h(prompt)==base[3]
 pd=json.loads(plan.read_text()); pd['generation_units'][0]['primary_action']='CORRUPT'; plan.write_text(json.dumps(pd)); prompt.write_text('CORRUPT'); m.regenerate(root,eid,'units'); assert (h(script),h(scenes))==base[:2] and h(plan)==base[2] and h(prompt)==base[3]
 sd=json.loads(scenes.read_text()); sd['scenes'][0]['purpose_description']='CORRUPT'; scenes.write_text(json.dumps(sd)); m.regenerate(root,eid,'scenes'); assert h(script)==base[0] and (h(scenes),h(plan),h(prompt))==base[1:]
 st=json.loads(script.read_text()); st['title']='CORRUPT'; script.write_text(json.dumps(st)); m.regenerate(root,eid,'script'); assert (h(script),h(scenes),h(plan),h(prompt))==base
 mem_after={p.name:h(p) for p in memdir.glob('*.json')} if memdir.exists() else {}; assert mem_before==mem_after
