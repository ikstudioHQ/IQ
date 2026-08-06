#!/usr/bin/env python3
from pathlib import Path
import zipfile,sys
from release_hygiene import is_prohibited
ROOT=Path(__file__).resolve().parents[1]
def package(out:Path):
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(x for x in ROOT.rglob('*') if x.is_file()):
   r=p.relative_to(ROOT)
   if is_prohibited(r) or (p.suffix.lower()=='.zip' and r.parts and r.parts[0]=='output_package'): continue
   info=zipfile.ZipInfo(r.as_posix(),(2026,8,5,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o100644<<16
   z.writestr(info,p.read_bytes(),compresslevel=9)
if __name__=='__main__': package(Path(sys.argv[1] if len(sys.argv)>1 else ROOT.parent/'Islamic_Kids_Studio_v2.72.zip'))
