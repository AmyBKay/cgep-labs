# GCP Baseline (Lab 5-4)

Terraform baseline configuration for project `cgep-lab-500208`, org `61099233299`.

## Contents
- `main.tf` — provider config, with `user_project_override` for ADC quota billing
- `org_policy.tf` — org policy constraints: disable SA key creation, require OS Login, uniform bucket-level access
- `wif.tf` — Workload Identity Federation for GitHub Actions, scoped to `AmyBKay/cgep-labs` only
- `audit_logs.tf` — Data Access audit logs (DATA_READ, DATA_WRITE, ADMIN_READ) for storage, KMS, and IAM
- `variables.tf` — input variables (`gcp_project`, `github_repo`)

## Usage
```bash
terraform init
terraform plan -var="gcp_project=cgep-lab-500208" -var="github_repo=AmyBKay/cgep-labs"
terraform apply -var="gcp_project=cgep-lab-500208" -var="github_repo=AmyBKay/cgep-labs"
```

## Verification performed
- Org policy enforcement confirmed by attempting service account key creation (blocked as expected)
- Audit logging confirmed by triggering a storage read and querying Cloud Logging
- Security Command Center checked — not provisioned at the org level; org policy constraints serve as the equivalent preventive control

## Evidence
See `evidence/lab-5-4/`:
- `org-policy-enforcement-test.txt`
- `audit-log-verification.json`
- `iam-policy.json`
- `scc-findings.json`
