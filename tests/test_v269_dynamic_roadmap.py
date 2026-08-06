from pathlib import Path
import sys,json,pytest,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.dynamic_roadmap import create,validate,revise,impact
from tools.episode_autopilot import generate,validate_package
@pytest.mark.parametrize('n',[1,7,30,90,365])
def test_dynamic_lengths(n): assert validate(create(n))['episode_count']==n
@pytest.mark.parametrize('n',[0,-1])
def test_invalid_lengths(n):
 with pytest.raises(ValueError): create(n)
def test_extend_shorten_versioning():
 r=create(7);x=revise(r,'extend',length=15);assert x['roadmap_version']==2 and len(x['episodes'])==15
 y=revise(x,'shorten',length=10);assert y['roadmap_version']==3 and len(y['episodes'])==10
def test_locked_shortening_fails():
 r=create(7);r['episodes'][-1]['status']='LOCKED'
 with pytest.raises(ValueError): revise(r,'shorten',length=6)
def test_broken_dependency_and_duplicate_fail():
 r=create(7);r['episodes'][1]['dependencies']=['missing']
 with pytest.raises(ValueError): validate(r)
 r=create(7);r['episodes'][1]['episode_id']=r['episodes'][0]['episode_id']
 with pytest.raises(ValueError): validate(r)
def test_impact_analysis():
 r=create(7);x=impact(r,r['episodes'][0]['episode_id']);assert x['direct_dependents']==[r['episodes'][1]['episode_id']]
def test_active_30_is_fresh_and_valid():
 r=json.loads((ROOT/'production/roadmaps/active_roadmap.json').read_text());assert validate(r)['episode_count']==30
 assert all(e['episode_id'].startswith('rm_') for e in r['episodes'])
def test_new_vertical_slices_generate(tmp_path):
 r=json.loads((ROOT/'production/roadmaps/active_roadmap.json').read_text())
 for e in (r['episodes'][0],r['episodes'][3],r['episodes'][4],r['episodes'][5]):
  q=generate(ROOT,e['episode_id'],outbase=tmp_path/e['episode_id']);assert q['generation_units']>0 and q['max_unit_duration']<=10
from tools.dynamic_roadmap import edit_future
def test_insert_replace_reorder_and_locked_protection():
 r=create(7); base=r['episodes'][3].copy(); base['episode_id']='rm_new_unique'; base['status']='ROADMAP_DRAFT'
 x=edit_future(r,'insert',position=3,replacement=base); assert len(x['episodes'])==8 and x['episodes'][2]['episode_id']=='rm_new_unique'
 repl=x['episodes'][4].copy(); repl['title']='Replacement Future Episode'; y=edit_future(x,'replace',episode_id=x['episodes'][4]['episode_id'],replacement=repl); assert y['episodes'][4]['title']=='Replacement Future Episode'
 z=edit_future(y,'reorder',episode_id=y['episodes'][5]['episode_id'],position=4); assert validate(z)['status']=='PASS'
 z['episodes'][0]['status']='LOCKED'
 with pytest.raises(ValueError): edit_future(z,'reorder',episode_id=z['episodes'][0]['episode_id'],position=2)
