"""Compiles the latest evidence per control into one audit-ready report."""
from datetime import datetime, timezone
from pathlib import Path
import yaml
from evidence_store import load_latest_evidence

REPORT_PATH = Path(__file__).parent / "data" / "evidence_report.md"


def load_control_catalog():
    catalog = yaml.safe_load((Path(__file__).parent / "controls_mapping.yaml").read_text())
    return {c["control_id"]: c for c in catalog["controls"]}


def generate_report():
    catalog = load_control_catalog()
    evidence = load_latest_evidence()

    lines = [
        "# Continuous Control Evidence Report",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "| Control | Title | SOC 2 | Status | Violations |",
        "|---|---|---|---|---|",
    ]
    for cid, c in catalog.items():
        r = evidence.get(cid)
        status = r["status"] if r else "NO DATA"
        count = len(r["violations"]) if r else "-"
        lines.append(f"| {cid} | {c['title']} | {c['frameworks']['soc2']} | {status} | {count} |")

    lines.append("\n---\n## Detailed Findings\n")
    for cid, c in catalog.items():
        r = evidence.get(cid)
        lines.append(f"### {cid}: {c['title']}\n{c['description']}")
        if not r:
            lines.append("_No evidence collected yet._\n")
            continue
        lines.append(f"**Status:** {r['status']} | **Checked:** {r['checked_at']}\n")
        if r["violations"]:
            for v in r["violations"]:
                resource = v.get("resource") or v.get("employee_id", "")
                lines.append(f"- ⚠️ `{resource}`: {v.get('issue', '')}")
        else:
            lines.append("- ✅ No violations found.")
        lines.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return REPORT_PATH


if __name__ == "__main__":
    print(f"Report written to {generate_report()}")
