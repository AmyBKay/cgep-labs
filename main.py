"""Runs the full continuous-controls pipeline: checks -> evidence -> report."""
from checks.access_review_check import run_all_access_checks
from checks.aws_checks import run_all_aws_checks
from evidence_store import store_all
from report_generator import generate_report


def main():
    print("Running AWS control checks (MFA, public buckets)...")
    aws_results = run_all_aws_checks()

    print("Running internal access review checks (HRIS cross-reference)...")
    access_results = run_all_access_checks()

    all_results = aws_results + access_results

    print("Storing evidence...")
    for p in store_all(all_results):
        print(f"  -> {p}")

    print("Generating audit-ready report...")
    print(f"  -> {generate_report()}")

    fail_count = sum(1 for r in all_results if r["status"] == "FAIL")
    print(f"\nDone. {len(all_results)} controls checked, {fail_count} with violations.")


if __name__ == "__main__":
    main()
