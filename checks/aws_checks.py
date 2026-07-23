"""Simulated-AWS checks. @mock_aws intercepts boto3 calls so nothing
touches a real cloud account. Swap it for a real boto3 session in prod."""
from datetime import datetime, timezone
import boto3
from moto import mock_aws


def _seed_fake_environment():
    iam = boto3.client("iam", region_name="us-east-1")
    s3 = boto3.client("s3", region_name="us-east-1")

    users_mfa = {"alice.admin": True, "bob.engineer": True, "carol.finance": False}
    for user, has_mfa in users_mfa.items():
        iam.create_user(UserName=user)
        if has_mfa:
            device = iam.create_virtual_mfa_device(VirtualMFADeviceName=f"{user}-mfa")["VirtualMFADevice"]
            iam.enable_mfa_device(UserName=user, SerialNumber=device["SerialNumber"],
                                   AuthenticationCode1="123456", AuthenticationCode2="123456")

    buckets_public = {"internal-artifacts": False, "customer-exports": True}
    for bucket, is_public in buckets_public.items():
        s3.create_bucket(Bucket=bucket)
        if is_public:
            s3.put_bucket_acl(Bucket=bucket, ACL="public-read")


def check_mfa_enforcement():
    iam = boto3.client("iam", region_name="us-east-1")
    users = iam.list_users()["Users"]
    violations = [
        {"resource": u["UserName"], "issue": "MFA not enabled"}
        for u in users if not iam.list_mfa_devices(UserName=u["UserName"])["MFADevices"]
    ]
    return {"control_id": "AC-01", "checked_at": datetime.now(timezone.utc).isoformat(),
            "resources_checked": len(users), "violations": violations,
            "status": "FAIL" if violations else "PASS"}


def check_public_buckets():
    s3 = boto3.client("s3", region_name="us-east-1")
    buckets = s3.list_buckets()["Buckets"]
    violations = []
    for b in buckets:
        for grant in s3.get_bucket_acl(Bucket=b["Name"])["Grants"]:
            if grant.get("Grantee", {}).get("URI", "").endswith("AllUsers"):
                violations.append({"resource": b["Name"], "issue": f"Public grant: {grant['Permission']}"})
    return {"control_id": "AC-02", "checked_at": datetime.now(timezone.utc).isoformat(),
            "resources_checked": len(buckets), "violations": violations,
            "status": "FAIL" if violations else "PASS"}


@mock_aws
def run_all_aws_checks():
    _seed_fake_environment()
    return [check_mfa_enforcement(), check_public_buckets()]


if __name__ == "__main__":
    import json
    print(json.dumps(run_all_aws_checks(), indent=2))
