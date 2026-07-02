## Chain of Custody: Property → Artifact Mapping

This lab wires cryptographic signing into the evidence pipeline so that chain
of custody is provable, not just asserted. Each of the four properties maps
to a specific artifact an auditor can independently check.

### Authenticity — "this evidence came from the claimed workflow"
**Artifact:** the `.sig.bundle` file, verified via `cosign verify-blob`.
Cosign's keyless signing uses the GitHub Actions OIDC token to prove the
signature was produced by this specific repo's workflow, with no private key
involved. Fulcio issues a short-lived certificate tied to that identity at
sign time. `verify-evidence.sh` checks this by validating the signature
against the OIDC issuer (`token.actions.githubusercontent.com`).

### Integrity — "this evidence hasn't changed since it was produced"
**Artifact:** the `.sha256` sidecar file, compared against a locally
recomputed hash. Any single-byte change to the bundle produces a completely
different SHA-256 digest. This was demonstrated directly: appending a single
line to a downloaded bundle changed its hash from the value recorded in
`evidence-28552504637-a00be41f26444a53d213a44bb223ad92dc662766.tar.gz.sha256`,
causing verification to fail.

### Timeliness — "there's a trustworthy record of when it was produced"
**Artifact:** the Rekor transparency log entry embedded inside the
`.sig.bundle`. Rekor timestamps the signature at the moment of signing, in a
public, append-only log that neither the signer nor an AWS admin can alter
after the fact. `cosign verify-blob` confirms this entry exists and is valid
as part of the same check that proves authenticity.

### Preservation — "it's still there, protected, when someone comes looking"
**Artifact:** the S3 Object Lock retention metadata on the stored bundle,
checked via `aws s3api get-object-retention`. The vault (deployed in Lab 2.5)
was configured with Object Lock, which prevents the object from being
deleted or overwritten until the retention date passes — confirmed when
attempting to re-upload a tampered copy of the bundle, which Object Lock
refused.

### End-to-end verification
Run `EVIDENCE_VAULT=cgep-lab-grc-evidence-vault-dae70b83 bash
scripts/verify-evidence.sh 28552504637 --profile default` to independently
confirm all four properties for run `28552504637`. Output:
```
Verified OK
...
CHAIN INTACT for run 28552504637
```
