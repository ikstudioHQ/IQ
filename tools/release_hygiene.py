#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,sys
from pathlib import Path
PROHIBITED_DIRS={'.git','.pytest_cache','__pycache__','.mypy_cache','.ruff_cache','.tox','.nox','.hypothesis','htmlcov','.venv','venv'}
PROHIBITED_NAMES={'.DS_Store','Thumbs.db','.coverage','.env'}
PROHIBITED_SUFFIXES={'.pyc','.pyo','.tmp','.temp','.bak','.swp','.swo'}
TEXT_SUFFIXES={'.md','.txt','.py','.json','.yaml','.yml','.toml','.ini','.cfg','.csv'}

def is_prohibited(p:Path): return any(x in PROHIBITED_DIRS for x in p.parts) or p.name in PROHIBITED_NAMES or p.suffix.lower() in PROHIBITED_SUFFIXES or (p.name.startswith('MASTER_PROMPT') and ('LOCAL_ONLY' in p.name or p.name=='MASTER_PROMPT.md'))

def classify(rel:Path):
 s=rel.as_posix()
 if is_prohibited(rel): return 'DEVELOPMENT_CACHE' if rel.suffix not in {'.pyc','.pyo'} else 'BYTECODE'
 if s.startswith('archive/'): return 'HISTORICAL_ARCHIVE'
 if s.startswith('tests/'): return 'ACTIVE_TEST'
 if s.startswith('tools/'): return 'ACTIVE_SOURCE'
 if s.startswith('docs/'): return 'ACTIVE_DOC'
 if s.startswith('generated/') or '/Gemini/' in s: return 'GENERATED_REQUIRED'
 if s.startswith('runtime/'): return 'GENERATED_REQUIRED'
 if s.startswith(('production/','phase','sources/','roadmap/','research/','psychology/')): return 'ACTIVE_PRODUCTION_DATA'
 if s.startswith(('assets/','examples/','output_package/')): return 'ACTIVE_ASSET'
 if rel.suffix=='.json': return 'ACTIVE_CONFIG'
 if rel.suffix in {'.md','.txt'}: return 'ACTIVE_DOC'
 return 'ACTIVE_SOURCE'

def scan(root:Path):
 files=[]; hashes={}; garbage=[]; bad_json=[]; zero=[]; abs_paths=[]
 for p in sorted(x for x in root.rglob('*') if x.is_file()):
  rel=p.relative_to(root); b=p.read_bytes(); h=hashlib.sha256(b).hexdigest(); c=classify(rel)
  files.append({'path':rel.as_posix(),'type':p.suffix.lower() or '<none>','bytes':len(b),'sha256':h,'category':c,'packaged_intentionally':not is_prohibited(rel)})
  hashes.setdefault(h,[]).append(rel.as_posix())
  if is_prohibited(rel): garbage.append(rel.as_posix())
  if len(b)==0: zero.append(rel.as_posix())
  if p.suffix.lower()=='.json':
   try: json.loads(b.decode('utf-8'))
   except Exception as e: bad_json.append({'path':rel.as_posix(),'error':str(e)})
  if p.suffix.lower() in TEXT_SUFFIXES:
   try:
    t=b.decode('utf-8')
    if re.search(r'(?i)(?:[A-Z]:\\Users\\|/mnt/data/|/home/[^/\s]+/)',t): abs_paths.append(rel.as_posix())
   except UnicodeDecodeError: pass
 dups=[v for v in hashes.values() if len(v)>1]
 return {'file_count':len(files),'files':files,'prohibited':garbage,'bad_json':bad_json,'zero_byte':zero,'absolute_path_files':abs_paths,'duplicate_groups':dups,'duplicate_bytes':sum((len(v)-1)*next(x['bytes'] for x in files if x['path']==v[0]) for v in dups)}

def main():
 root=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1]).resolve(); r=scan(root)
 print(json.dumps({k:v for k,v in r.items() if k!='files'},indent=2)); sys.exit(1 if r['prohibited'] or r['bad_json'] else 0)
if __name__=='__main__': main()
