"""Simulates an HRIS and an internal access system — the kind of homegrown
tooling that off-the-shelf GRC platforms have no pre-built connector for."""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

fake = Faker()
random.seed(3)
Faker.seed(3)
OUT_DIR = Path(__file__).parent
NOW = datetime(2026, 7, 22)

def generate_hris(n=20):
    employees = []
    for i in range(1, n + 1):
        terminated = random.random() < 0.2
        term_date = (NOW - timedelta(days=random.randint(1, 60))).isoformat() if terminated else None
        employees.append({
            "employee_id": f"EMP-{i:03d}",
            "name": fake.name(),
            "status": "terminated" if terminated else "active",
            "termination_date": term_date,
        })
    return employees

def generate_internal_access(employees):
    terminated_by_id = {e["employee_id"]: e for e in employees if e["status"] == "terminated"}
    access = []
    for emp in employees:
        if random.random() > 0.4:
            continue
        granted = NOW - timedelta(days=random.randint(30, 400))
        stale = random.random() < 0.35
        reviewed_days_ago = random.randint(91, 200) if stale else random.randint(1, 89)

        record = {
            "employee_id": emp["employee_id"],
            "resource": "prod-sensitive-customer-db",
            "granted_date": granted.isoformat(),
            "last_reviewed_date": (NOW - timedelta(days=reviewed_days_ago)).isoformat(),
            "access_revoked_date": None,
        }

        # If this employee is terminated, decide how their revocation played out:
        # some revoked on time, some revoked late, some never revoked at all.
        if emp["employee_id"] in terminated_by_id:
            term_date = datetime.fromisoformat(terminated_by_id[emp["employee_id"]]["termination_date"])
            outcome = random.random()
            if outcome < 0.4:
                # Revoked within SLA (a few hours after termination)
                record["access_revoked_date"] = (term_date + timedelta(hours=random.randint(1, 20))).isoformat()
            elif outcome < 0.7:
                # Revoked late — days after termination
                record["access_revoked_date"] = (term_date + timedelta(days=random.randint(2, 15))).isoformat()
            # else: never revoked, access_revoked_date stays None — ongoing violation

        access.append(record)
    return access

if __name__ == "__main__":
    employees = generate_hris()
    access = generate_internal_access(employees)
    (OUT_DIR / "hris.json").write_text(json.dumps(employees, indent=2))
    (OUT_DIR / "internal_access.json").write_text(json.dumps(access, indent=2))
    print(f"{len(employees)} employees, {len(access)} access records generated.")
