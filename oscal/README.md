OSCAL Artifacts

Components

compliant-s3.json: Component definition for the compliant-s3 Terraform module
(terraform/primitives/compliant-s3). Describes implementation of NIST 800-53 Rev 5
controls SC-28, AC-3, AU-3, and CM-6, each mapped to the specific Terraform resource
that enforces it. Evidence for each control is a signed pipeline bundle stored in the
Lab 2.5 evidence vault (cgep-lab-grc-evidence-vault-dae70b83).

Profiles

cge-p-minimum.json: Minimum control selection profile, importing SC-28, AC-3,
AU-3, and CM-6 from the NIST SP 800-53 Rev 5 catalog.

Validation

trestle validate results for the component definition are captured at
evidence/lab-6-1/trestle-validate.txt.

Evidence traversal

Verified end-to-end chain of custody for run 28552504637 using
evidence/lab-4-4/verify-evidence.sh: SHA256 integrity and cosign signature/Rekor
timestamp both passed. Object Lock retention on that specific run had since expired,
so preservation could not be re-confirmed at time of this write-up.
