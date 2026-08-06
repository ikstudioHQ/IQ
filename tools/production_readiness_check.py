#!/usr/bin/env python3
"""Aggregate production-readiness gate. Fails if any required repository-native gate fails."""
import json,re,subprocess,sys
from pathlib import Path
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()

def run(label, cmd):
    p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
    print(f"[{label}] exit={p.returncode}")
    if p.stdout: print(p.stdout.rstrip())
    if p.stderr: print(p.stderr.rstrip())
    return p.returncode==0

def version_checks():
    manifest=json.loads((ROOT/'repository_manifest.json').read_text())['repository_version']
    vc=(ROOT/'VERSION_COMPATIBILITY.md').read_text()
    m=re.search(r'Current Repository Version:\s*\*\*v([^*]+)\*\*',vc)
    expected=m.group(1) if m else None
    vals={
      'repository_manifest.json':manifest,
      'generated/repository_fingerprint.json':json.loads((ROOT/'generated/repository_fingerprint.json').read_text())['repository_version'],
      'runtime/runtime_manifest.json':json.loads((ROOT/'runtime/runtime_manifest.json').read_text())['repository_version'],
    }
    bad={k:v for k,v in vals.items() if v!=expected}
    print(f"[VERSION CONSISTENCY] expected={expected} values={vals}")
    return not bad

def fingerprint_fresh():
    fp=json.loads((ROOT/'generated/repository_fingerprint.json').read_text())
    ignored={'.git','__pycache__','.pytest_cache'}
    actual=sum(1 for p in ROOT.rglob('*') if p.is_file() and not any(x in ignored for x in p.parts) and p.name!='.protected_snapshot.json')
    print(f"[FINGERPRINT] recorded_total_files={fp.get('total_files')} actual_total_files={actual}")
    return fp.get('total_files')==actual

ok=True
ok &= run('REPOSITORY VALIDATOR',[sys.executable,'tools/validate_repo.py','.'])
ok &= run('PREFLIGHT',[sys.executable,'tools/preflight_check.py','.'])
ok &= run('PYTEST',[sys.executable,'-m','pytest','-q'])
ok &= version_checks()
ok &= fingerprint_fresh()
ok &= run('EPISODE COMPILER',[sys.executable,'tools/compile_gemini_episodes.py'])
for ep in ['ep_honesty_wallet_assisted','ep_tawakkul_lost_toy']:
    ok &= run(f'EPISODE CONSISTENCY {ep}',[sys.executable,'tools/episode_consistency_check.py','check-episode',f'output_package/{ep}','.'])
    p=subprocess.run([sys.executable,'tools/package_episode.py',ep,'--final'],cwd=ROOT,text=True,capture_output=True)
    print(f'[FINAL-PACKAGE FAIL-CLOSED {ep}] exit={p.returncode}')
    print((p.stdout+p.stderr).rstrip())
    ok &= p.returncode != 0 and 'FINAL PUBLICATION PACKAGE BLOCKED' in (p.stdout+p.stderr)
print('PRODUCTION_READINESS: PASS' if ok else 'PRODUCTION_READINESS: FAIL')
sys.exit(0 if ok else 1)
