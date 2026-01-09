import yaml
import re
import os

def load_policies():
    candidates = [
        "policies/governance_rules.yaml",
        "policies/governance_rules.yml",
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path) as f:
                return yaml.safe_load(f)

    # Fallback defaults (safe, conservative defaults)
    return {
        "disallowed_cidrs": ["0.0.0.0/0"],
        "max_instance_types": {
            "allowed": ["t2.micro", "t3.micro", "t3a.micro"]
        }
    }

POLICIES = load_policies()

def check_open_cidrs(terraform_diff):
    issues = []
    for cidr in POLICIES.get("disallowed_cidrs", []):
        if cidr in terraform_diff:
            issues.append(f"🚨 Open CIDR detected: {cidr}")
    return issues

def check_instance_size(terraform_diff):
    issues = []
    if "instance_type" in terraform_diff:
        match = re.search(r'instance_type\s*=\s*"([^"]+)"', terraform_diff)
        if match:
            instance_type = match.group(1)
            allowed = POLICIES.get("max_instance_types", {}).get("allowed", [])
            if instance_type not in allowed:
                issues.append(f"💰 Instance type `{instance_type}` may be costly")
    return issues
