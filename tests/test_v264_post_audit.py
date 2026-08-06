import json, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def run_pkg(root, slug='ep_tawakkul_lost_toy'):
    return subprocess.run([sys.executable,'tools/package_episode.py',slug,'--final'],cwd=root,text=True,capture_output=True)

def test_final_blocks_even_if_review_queue_is_forged_approved(tmp_path):
    dst=tmp_path/'repo'; shutil.copytree(ROOT,dst)
    p=dst/'phase2/data/database/review_queue.json'; d=json.loads(p.read_text())
    for e in d['episodes']:
        if e.get('episode_id')=='ep_tawakkul_lost_toy': e['status']='approved'
    p.write_text(json.dumps(d,indent=2))
    r=run_pkg(dst); assert r.returncode!=0
    out=r.stdout+r.stderr
    assert ('religious-source publication gate' in out or 'semantic support remains unclassified' in out)

def test_final_blocks_missing_review_queue(tmp_path):
    dst=tmp_path/'repo'; shutil.copytree(ROOT,dst)
    (dst/'phase2/data/database/review_queue.json').unlink()
    r=run_pkg(dst); assert r.returncode!=0

def test_local_master_version_matches_when_supplied():
    p=ROOT/'MASTER_PROMPT.md'
    if not p.exists():
        return  # valid distribution profile
    text=p.read_text()
    assert '**Version:** 2.64' in text
