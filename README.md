# Continuous Controls Monitoring — GRC Automation Demo

A local, runnable demo of **policy-as-code / continuous control testing** —
pulling compliance evidence directly from systems via API instead of
collecting screenshots manually before an audit.

## The problem

Off-the-shelf GRC platforms (Vanta, Drata, Secureframe) have great native
integrations for common systems — AWS, Okta, GitHub. But they have **no
integration for a company's homegrown internal tools**.

| Control | Data source | Platform-native? |
|---|---|---|
| MFA enforced for privileged users | AWS IAM | ✅ Common integration |
| No public S3 buckets | AWS S3 | ✅ Common integration |
| Access revoked within 24h of termination | Internal access system + HRIS | ❌ Custom code required |
| Access reviewed every 90 days | Internal access system | ❌ Custom code required |

## Architecture

```
main.py
 ├── checks/aws_checks.py          -> simulated-AWS checks (via moto)
 ├── checks/access_review_check.py -> custom checks vs. mock internal systems
 ├── evidence_store.py             -> persists timestamped, control-mapped evidence
 ├── report_generator.py           -> compiles evidence into an audit-ready report
 └── controls_mapping.yaml         -> one control catalog mapped to SOC 2 + ISO 27001
```

## Running it

```bash
pip install -r requirements.txt
python3 mock_data/generate_mock_data.py   # (already included, regenerate for new data)
python3 main.py                           # run checks -> evidence -> report
python3 -m pytest tests/ -v               # run tests
```

Output: `data/evidence/*.json` (raw timestamped evidence) and
`data/evidence_report.md` (the compiled report).

## Why `moto`

`moto` intercepts boto3 calls and simulates AWS in memory — zero cost, zero
credentials, reproducible results. In production, swap `@mock_aws` for a
real read-only boto3 session; the check logic doesn't change.

## Extensions

- Point AWS checks at a real free-tier sandbox account instead of `moto`
- Push evidence into a real GRC platform via its API
- Add a Slack alert when a control flips PASS -> FAIL
- Add a control for agent/LLM access to production systems
