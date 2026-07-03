# Lab 4.3: AWS OIDC Trust + tfsec Policy Gate

## What this lab covers

Two things that work together in the CI/CD pipeline:

1. **Keyless AWS authentication** for GitHub Actions via OpenID Connect (OIDC) —
   no long-lived AWS access keys stored as GitHub secrets.
2. **A tfsec policy gate** in the pipeline that scans Terraform plans for security
   findings and fails the build on high/critical issues, before anything gets applied.

## OIDC Trust Setup

`terraform/primitives/oidc-trust/main.tf` provisions:

- An `aws_iam_openid_connect_provider` trusting GitHub's OIDC issuer
  (`token.actions.githubusercontent.com`)
- An IAM role (`cgep-grc-gate`) that can only be assumed via
  `sts:AssumeRoleWithWebIdentity`, gated by two conditions:
  - `aud` must equal `sts.amazonaws.com` (token was minted for AWS STS specifically)
  - `sub` must match `repo:${github_org}/${github_repo}:*` (token must come from
    this specific repository — no other GitHub repo can assume this role)

This is the AWS equivalent of the `attribute_condition` used in the GCP Workload
Identity Federation setup (Lab 5.4) — same principle, different cloud: trust is
scoped to exactly one repository, not left open to any caller with a valid OIDC token.

The role is attached to `ReadOnlyAccess` only — the pipeline can inspect and plan,
not mutate, infrastructure.

## The tfsec Gate

`.github/workflows/grc-gate.yml` runs on every PR:

1. Assumes the `cgep-grc-gate` role via OIDC (no stored credentials)
2. Runs `terraform init` / `terraform plan`
3. Runs a Conftest policy gate (Lab 3.4) against the plan
4. Runs a **tfsec scan** and fails the build on high/critical findings
5. Uploads evidence artifacts (`plan.json`, `conftest-results.json`, `tfsec.sarif`)

## Proof the gate actually works

This isn't theoretical — the gate caught a real finding during pipeline testing.
A demo PR removed S3 encryption configuration to intentionally trigger a violation:

- **Red PR**: encryption config removed → tfsec flagged a HIGH severity finding
- **Fix**: commit `1afce6e` — *"fix: use customer-managed KMS key for S3 encryption
  (resolves tfsec HIGH finding)"* — restored compliant encryption using a
  customer-managed KMS key
- **Green PR**: re-ran clean, gate passed

This demonstrates the control isn't just present in code — it was exercised against
a real violation and correctly blocked it until remediated, the same enforcement
pattern verified in Lab 5.4 with GCP Org Policy.

## Evidence

- `terraform/primitives/oidc-trust/main.tf` — OIDC provider + scoped trust role
- `.github/workflows/grc-gate.yml` — pipeline definition (OIDC auth, Conftest, tfsec, evidence upload)
- Commit `1afce6e` on `red-pr-demo` — real tfsec HIGH finding caught and remediated
- Commit `e388de9` — OIDC trust fix applied mid-pipeline, confirming the auth flow was
  actively debugged and validated end-to-end, not just written and left untested

## Note on lab sequencing

This work was originally built as shared CI/CD
