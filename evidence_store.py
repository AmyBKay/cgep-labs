"""Persists each control check result as a timestamped evidence file.
This is what an auditor actually reviews — not the live script output."""
import json
from datetime import datetime, timezone
from pathlib import Path

EVIDENCE_DIR = Path(__file__).parent / "data" / "evidence"


def store_evidence(result: dict):
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filepath = EVIDENCE_DIR / f"{result['control_id']}_{ts}.json"
    filepath.write_text(json.dumps(result, indent=2))
    return filepath


def store_all(results: list[dict]):
    return [store_evidence(r) for r in results]


def load_latest_evidence():
    if not EVIDENCE_DIR.exists():
        return {}
    latest = {}
    for filepath in sorted(EVIDENCE_DIR.glob("*.json")):
        record = json.loads(filepath.read_text())
        latest[record["control_id"]] = record
    return latest
