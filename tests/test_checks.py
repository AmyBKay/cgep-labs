import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from checks.aws_checks import run_all_aws_checks
from checks.access_review_check import check_terminated_access, check_stale_reviews


def test_aws_checks_detect_seeded_violations():
    results = run_all_aws_checks()
    mfa = next(r for r in results if r["control_id"] == "AC-01")
    buckets = next(r for r in results if r["control_id"] == "AC-02")
    assert mfa["status"] == "FAIL" and len(mfa["violations"]) == 1
    assert buckets["status"] == "FAIL" and len(buckets["violations"]) == 1


def test_terminated_access_check_detects_unrevoked_access():
    result = check_terminated_access()
    assert result["control_id"] == "AC-03"
    # With the fixed mock data seed, EMP-010 is terminated with no
    # access_revoked_date on file — access was never revoked.
    assert result["status"] == "FAIL"
    flagged_ids = {v["employee_id"] for v in result["violations"]}
    assert "EMP-010" in flagged_ids


def test_stale_review_check_runs():
    result = check_stale_reviews()
    assert result["control_id"] == "AC-04"
    assert result["status"] in ("PASS", "FAIL")


if __name__ == "__main__":
    test_aws_checks_detect_seeded_violations()
    test_terminated_access_check_detects_unrevoked_access()
    test_stale_review_check_runs()
    print("All tests passed.")
