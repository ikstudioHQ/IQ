#!/usr/bin/env python3
"""Deterministically regenerate generated/repository_fingerprint.json from live repository state."""
import json, os, sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

def load(rel):
    return json.loads((ROOT/rel).read_text(encoding="utf-8"))

def list_count(rel, key):
    d=load(rel); return len(d.get(key, []))

def repository_files():
    ignored={'.git','__pycache__','.pytest_cache'}
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and not any(x in ignored for x in p.parts) and p.name not in {'.protected_snapshot.json','MASTER_PROMPT.md'} and '/Gemini/' not in ('/'+p.relative_to(ROOT).as_posix()) and not (p.suffix.lower()=='.zip' and p.relative_to(ROOT).parts[0]=='output_package'))

chars=load('sources/characters/character_master_library.json').get('characters',[])
islamic={}
for p in (ROOT/'phase2/data/islamic').glob('*.json'):
    d=json.loads(p.read_text(encoding='utf-8'))
    for k,v in d.items():
        if isinstance(v,list): islamic[k]=v
concepts=list((ROOT/'phase3/knowledge/concepts').glob('*.json'))
loc=load('sources/production/location_library.json').get('locations',[])
ward=load('sources/production/wardrobe_library.json').get('wardrobes',[])
props=load('sources/production/prop_registry.json').get('props',[])
safety=load('phase2/data/safety/content_scene_safety_registry.json').get('rules',[])
ep=load('phase5/orchestration/planning/episode_topic_bank.json').get('topics',[])
sg=load('phase5/orchestration/planning/song_topic_bank.json').get('song_topics',[])
manifest=load('repository_manifest.json')
out={
 'generated_from':'computed live from canonical sources -- regenerate, never hand-edit',
 'repository_version':manifest['repository_version'],
 'architecture_status':'FROZEN','content_safety_status':'FROZEN','publication_gate_status':'FROZEN',
 'characters_total':len(chars),'characters_speaking':sum(bool(c.get('is_speaking')) for c in chars),'characters_non_speaking':sum(not bool(c.get('is_speaking')) for c in chars),
 'quran_verses':len(islamic.get('verses',[])), 'hadith':len(islamic.get('hadith_entries',[])), 'duas':len(islamic.get('duas',[])),
 'prophets':len(islamic.get('prophets',[])), 'concepts':len(concepts),
 'vocabulary':list_count('phase2/data/language/pronunciation_dictionary.json','words'),
 'conflicts':list_count('phase3/knowledge/story/conflict_library.json','conflicts'),
 'patterns':list_count('phase3/knowledge/story/story_patterns.json','patterns'),
 'locations':len(loc),'wardrobes':len(ward),'props':len(props),'safety_rules':len(safety),
 'episode_topics':len(ep),'song_topics':len(sg),
 'published_episodes':sum(t.get('status')=='published' for t in ep),'published_songs':sum(t.get('status')=='published' for t in sg),
 'total_files':len(repository_files())
}
path=ROOT/'generated/repository_fingerprint.json'
path.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f"Generated {path.relative_to(ROOT)}: version={out['repository_version']} total_files={out['total_files']}")
