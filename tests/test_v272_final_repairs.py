import hashlib, importlib.util, json, shutil
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
def load(rel,name):
 spec=importlib.util.spec_from_file_location(name,ROOT/rel); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def gate_fixture(tmp_path,monkeypatch,text,entry=None):
 m=load('tools/package_episode.py','pegate'); monkeypatch.chdir(tmp_path); d=tmp_path/'output_package'/'ep'; d.mkdir(parents=True); (d/'verification_report.md').write_text(text)
 monkeypatch.setattr(m,'islamic_entries_by_id',lambda: {} if entry is None else {'ev1':entry}); return m
@pytest.mark.parametrize('entry,needle',[
 ({'citation_verified':False,'source_verified':True,'scholarly_reviewed':True},'citation/source'),
 ({'citation_verified':True,'source_verified':False,'scholarly_reviewed':True},'citation/source'),
 ({'citation_verified':True,'source_verified':True,'scholarly_reviewed':False},'scholarly_reviewed')])
def test_deep_final_gate_individual_truth_failures(tmp_path,monkeypatch,entry,needle):
 m=gate_fixture(tmp_path,monkeypatch,'Evidence: ev1\n',entry); ok,p=m.final_religious_gate('ep'); assert not ok and needle in p[0]
def test_deep_final_gate_missing_unknown_malformed(tmp_path,monkeypatch):
 m=gate_fixture(tmp_path,monkeypatch,'No evidence field here\n'); assert m.final_religious_gate('ep')[0] is False
 (tmp_path/'output_package/ep/verification_report.md').write_text('Evidence: ev1 extra\n'); assert m.final_religious_gate('ep')[0] is False
 (tmp_path/'output_package/ep/verification_report.md').write_text('Evidence: unknown\n'); ok,p=m.final_religious_gate('ep'); assert not ok and 'does not resolve' in p[0]
def test_deep_final_gate_forged_surrounding_approvals_do_not_bypass(tmp_path,monkeypatch):
 # Queue/semantic forgeries are deliberately outside the deepest evidence gate; they cannot turn false evidence true.
 m=gate_fixture(tmp_path,monkeypatch,'Evidence: ev1\n',{'citation_verified':False,'source_verified':False,'scholarly_reviewed':False})
 (tmp_path/'phase2/data/database').mkdir(parents=True); (tmp_path/'phase2/data/database/review_queue.json').write_text(json.dumps({'episodes':[{'episode_id':'ep','status':'approved'}]}))
 (tmp_path/'forged_semantic.json').write_text(json.dumps({'semantic_support':'SUPPORTED','approved':True}))
 ok,p=m.final_religious_gate('ep'); assert not ok and p
 # combined forgery still cannot bypass
 (tmp_path/'phase2/data/safety').mkdir(parents=True); (tmp_path/'phase2/data/safety/review_resolutions.json').write_text(json.dumps({'resolutions':[{'episode_id':'ep','resolved_decision':'ALLOW'}]}))
 assert m.final_religious_gate('ep')[0] is False
def test_deep_final_gate_controlled_success(tmp_path,monkeypatch):
 m=gate_fixture(tmp_path,monkeypatch,'Evidence: ev1\n',{'citation_verified':True,'source_verified':True,'scholarly_reviewed':True}); assert m.final_religious_gate('ep')==(True,[])
def setup_ep(tmp_path):
 root=tmp_path/'repo'; shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','__pycache__','.pytest_cache')); m=load(root/'tools/episode_autopilot.py','eafinal'); eid=json.loads((root/'production/roadmaps/active_roadmap.json').read_text())['episodes'][0]['episode_id']; m.generate(root,eid); return root,m,eid
def artifacts(root,eid):
 b=root/'production/autopilot/episodes'/eid; return b,[b/'story_script.json',b/'logical_scenes.json',*sorted((b/'production_plans').glob('*.json')),*sorted((b/'gemini').glob('*.md'))]
def test_stage_regeneration_full_hash_contract_and_memory(tmp_path):
 root,m,eid=setup_ep(tmp_path); b,paths=artifacts(root,eid); script,scenes=paths[:2]; plans=sorted((b/'production_plans').glob('*.json')); prompts=sorted((b/'gemini').glob('*.md')); mem=root/'production/intelligence/accepted_memory'; before_mem={str(p.relative_to(root)):h(p) for p in mem.rglob('*') if p.is_file()} if mem.exists() else {}
 baseline={'script':h(script),'scenes':h(scenes),'plans':[h(p) for p in plans],'prompts':[h(p) for p in prompts]}
 prompts[0].write_text('bad'); m.regenerate(root,eid,'prompts'); assert h(script)==baseline['script'] and h(scenes)==baseline['scenes'] and [h(p) for p in plans]==baseline['plans'] and [h(p) for p in prompts]==baseline['prompts']
 plans[0].write_text('{bad')
 with pytest.raises(ValueError): m.regenerate(root,eid,'prompts')
 m.regenerate(root,eid,'units'); assert h(script)==baseline['script'] and h(scenes)==baseline['scenes'] and [h(p) for p in plans]==baseline['plans']
 scenes.write_text('{bad')
 with pytest.raises(ValueError): m.regenerate(root,eid,'units')
 scenes.write_text(json.dumps(m._scenes(root,json.loads(script.read_text()),600),indent=2))
 m.regenerate(root,eid,'scenes'); assert h(script)==baseline['script'] and h(scenes)==baseline['scenes']
 script.write_text('{bad')
 with pytest.raises(ValueError): m.regenerate(root,eid,'scenes')
 # script stage rebuilds from roadmap and downstream; corrupt script is intentionally replaceable.
 m.regenerate(root,eid,'script'); assert h(script)==baseline['script'] and h(scenes)==baseline['scenes'] and [h(p) for p in plans]==baseline['plans'] and [h(p) for p in prompts]==baseline['prompts']
 after_mem={str(p.relative_to(root)):h(p) for p in mem.rglob('*') if p.is_file()} if mem.exists() else {}; assert before_mem==after_mem
def test_stage_changed_upstream_dependency_rebuilds_downstream(tmp_path):
 root,m,eid=setup_ep(tmp_path); b,_=artifacts(root,eid); script=b/'story_script.json'; scenes=b/'logical_scenes.json'; plans=sorted((b/'production_plans').glob('*.json')); prompts=sorted((b/'gemini').glob('*.md')); old=(h(scenes),[h(p) for p in plans],[h(p) for p in prompts])
 d=json.loads(script.read_text()); d['evidence_ids']=['temporary_fixture_evidence']; script.write_text(json.dumps(d,indent=2)); m.regenerate(root,eid,'scenes'); new=(h(scenes),[h(p) for p in plans],[h(p) for p in prompts]); assert new!=old and h(script)==hashlib.sha256(script.read_bytes()).hexdigest()
def test_invalid_episode_and_stage_fail_closed(tmp_path):
 root,m,eid=setup_ep(tmp_path)
 with pytest.raises(ValueError): m.regenerate(root,'not_an_episode','script')
 with pytest.raises(ValueError): m.regenerate(root,eid,'bogus')
def test_health_report_generation_is_byte_deterministic(tmp_path):
 m=load('tools/validate_repo.py','vrfinal'); root=tmp_path/'repo'; shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','__pycache__','.pytest_cache')); files=m.find_all_files(str(root)); e=['z','a']; w=['z','a']; m.write_health_report(str(root),files,e,w); first=h(root/'REPO_HEALTH_REPORT.md'); m.write_health_report(str(root),list(reversed(files)),list(reversed(e)),list(reversed(w))); assert h(root/'REPO_HEALTH_REPORT.md')==first

def test_stage_missing_intermediates_fail_or_rebuild_by_contract(tmp_path):
 root,m,eid=setup_ep(tmp_path); b,_=artifacts(root,eid); script=b/'story_script.json'; scenes=b/'logical_scenes.json'; plan=sorted((b/'production_plans').glob('*.json'))[0]
 plan.unlink()
 with pytest.raises(ValueError): m.regenerate(root,eid,'prompts')
 m.regenerate(root,eid,'units'); assert plan.exists()
 scenes.unlink()
 with pytest.raises(ValueError): m.regenerate(root,eid,'units')
 # script stage owns all downstream and can reconstruct a missing scenes artifact using the default target only if prior target is unavailable; current contract fails closed because target metadata is missing.
 with pytest.raises(ValueError): m.regenerate(root,eid,'script')
 script.unlink()
 with pytest.raises(ValueError): m.regenerate(root,eid,'scenes')
