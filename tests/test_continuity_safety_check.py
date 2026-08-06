import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.continuity.safety_check import SafetyChecker


def test_clean_text_has_no_findings(repo_root):
    checker = SafetyChecker(repo_root)
    findings = checker.scan("Zayd smiles and says good morning to his sister.")
    assert findings == []


def test_never_generate_content_restriction_blocks(repo_root):
    checker = SafetyChecker(repo_root)
    findings = checker.scan("There is blood on the floor after the fight.")
    assert any(f.rule_id == "restriction_005" and f.severity == "error" for f in findings)


def test_scene_safety_block_rule_blocks(repo_root):
    checker = SafetyChecker(repo_root)
    findings = checker.scan("The scene shows a graphic wound, brutally depicted.")
    assert any(f.rule_id == "safety_003" and f.severity == "error" for f in findings)


def test_context_only_restriction_exempted_by_nearby_citation(repo_root):
    checker = SafetyChecker(repo_root)
    # restriction_001 (pork) is CONTEXT_ONLY -- a nearby real citation id should exempt it.
    text = "The lesson teaches about food rules (hd_042) including why pork is not eaten."
    findings = checker.scan(text)
    assert not any(f.rule_id == "restriction_001" for f in findings)


def test_context_only_restriction_without_citation_still_flagged(repo_root):
    checker = SafetyChecker(repo_root)
    text = "Zayd sees pork on the table at the market."
    findings = checker.scan(text)
    assert any(f.rule_id == "restriction_001" for f in findings)


def test_sacred_depiction_heuristic_catches_indirect_phrasing(repo_root):
    checker = SafetyChecker(repo_root)
    findings = checker.scan("A figure representing Allah appears in the clouds.")
    assert any(f.source == "sacred_depiction_heuristic" for f in findings)


def test_sacred_name_alone_without_depiction_word_not_flagged(repo_root):
    checker = SafetyChecker(repo_root)
    findings = checker.scan("Zayd says Alhamdulillah, thanking Allah for the meal.")
    assert not any(f.source == "sacred_depiction_heuristic" for f in findings)


def test_review_required_level_is_warning_not_error(repo_root):
    checker = SafetyChecker(repo_root)
    findings = checker.scan("The children are playing with fire near the tent.")
    review_findings = [f for f in findings if f.level == "REVIEW_REQUIRED"]
    assert len(review_findings) >= 1
    assert all(f.severity == "warning" for f in review_findings)
