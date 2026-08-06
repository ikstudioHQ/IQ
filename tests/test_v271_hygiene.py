from pathlib import Path
import importlib.util,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('release_hygiene',ROOT/'tools/release_hygiene.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def test_packaging_prohibited_patterns():
 for x in ['.pytest_cache/x','a/__pycache__/x.pyc','x.pyc','x.tmp','x.bak','.DS_Store','Thumbs.db','.env']:
  assert m.is_prohibited(Path(x))
def test_current_tree_has_no_prohibited_files():
    # Phase 8 audit finding (independently reproduced, not carried forward
    # from prior phases): __pycache__/ and .pytest_cache/ are created by
    # the act of running pytest itself, so scanning ROOT from *inside* a
    # live pytest session will always find them regardless of repo
    # cleanliness -- this is a self-referential test-harness defect, not
    # a real content leak. Both are already in .gitignore and already
    # excluded from packaging by is_prohibited() (see
    # tools/orchestration/season_packager.py and this same function).
    # This narrows the check to what it can actually validate mid-session
    # -- everything else prohibited (.env, .DS_Store, stray .pyc outside
    # a cache dir, etc.) still fails this test immediately, unchanged.
    prohibited = m.scan(ROOT)['prohibited']
    real_findings = [p for p in prohibited if '__pycache__' not in p and '.pytest_cache' not in p]
    assert not real_findings
def test_all_json_parse(): assert not m.scan(ROOT)['bad_json']
def test_core_import_origin_is_local():
 import tools.production_intelligence as x
 assert Path(x.__file__).resolve().is_relative_to(ROOT)
