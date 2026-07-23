\# Compliance Policies



OPA/Rego policies implementing NIST 800-53 controls.



| File | Control | Description |

|------|---------|-------------|

| sc28\_encryption.rego | SC-28 | GCS buckets must use CMEK |

| sc28\_encryption\_aws.rego | SC-28 | S3 buckets must have server-side encryption |

| ac3\_no\_public.rego | AC-3 | GCS buckets and firewalls must not allow public access |

| ac3\_no\_public\_aws.rego | AC-3 | S3 buckets must block public access |

| cm6\_required\_tags.rego | CM-6 | GCP resources must have required labels |

| cm6\_required\_tags\_aws.rego | CM-6 | AWS resources must have required tags |

