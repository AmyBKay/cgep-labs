"""Custom control logic: cross-references the internal access system
against HRIS termination data. No GRC platform has a connector for
either of these homegrown systems, so this join has to be written by hand."""
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "mock_data"
NOW = datetime(2026, 7, 22)
REVOCATION_SLA_HOURS = 24
REVIEW_SLA_DAYS = 90


def _load():
    employees = json.loads((DATA_DIR / "hris.json").read_text())
    access = json.loads((DATA_DIR / "internal_access.json").read_text())
    return employees, access


def check_terminated_access():
    employees, access = _load()
    terminated = {e["employee_id"]: e for e in employees if e["status"] == "terminated"}
    access_by_id = {a["employee_id"]: a for a in access}

    violations = []
    for emp_id in access_by_id.keys() & terminated.keys():
        term_date = datetime.fromisoformat(terminated[emp_id]["termination_date"])
        revoked_date_str = access_by_id[emp_id].get("access_revoked_date")

        if revoked_date_str is None:
            # Never revoked at all — the record still shows active access
            # with no revocation event on file. This is the worst case.
            hours_open = (NOW - term_date).total_seconds() / 3600
            violations.append({
                "employee_id": emp_id, "name": terminated[emp_id]["name"],
                "issue": f"Access never revoked — terminated {hours_open/24:.1f} days ago, still active",
            })
        else:
            # Revoked at some point — measure the actual gap between
            # termination and revocation against the 24h SLA.
            revoked_date = datetime.fromisoformat(revoked_date_str)
            hours_to_revoke = (revoked_date - term_date).total_seconds() / 3600
            if hours_to_revoke > REVOCATION_SLA_HOURS:
                violations.append({
                    "employee_id": emp_id, "name": terminated[emp_id]["name"],
                    "issue": f"Revoked {hours_to_revoke:.1f}h after termination (SLA: {REVOCATION_SLA_HOURS}h)",
                })
            # else: revoked within SLA — compliant, no violation

    return {"control_id": "AC-03", "checked_at": NOW.isoformat(), "resources_checked": len(access),
            "violations": violations, "status": "FAIL" if violations else "PASS"}


def check_stale_reviews():
    _, access = _load()
    violations = []
    for record in access:
        days_since = (NOW - datetime.fromisoformat(record["last_reviewed_date"])).days
        if days_since > REVIEW_SLA_DAYS:
            violations.append({
                "employee_id": record["employee_id"],
                "issue": f"Last reviewed {days_since} days ago (SLA: {REVIEW_SLA_DAYS})",
            })
    return {"control_id": "AC-04", "checked_at": NOW.isoformat(), "resources_checked": len(access),
            "violations": violations, "status": "FAIL" if violations else "PASS"}


def run_all_access_checks():
    return [check_terminated_access(), check_stale_reviews()]


if __name__ == "__main__":
    import json as j
    print(j.dumps(run_all_access_checks(), indent=2))
