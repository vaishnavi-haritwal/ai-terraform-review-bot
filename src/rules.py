import yaml
import re

with open("policies/governance_rules.yaml") as f:
    POLICIES = yaml.safe_load(f)

def check_open_cidrs(terraform_diff):
    issues = []
    for cidr in POLICIES["disallowed_cidrs"]:
        if cidr in terraform_diff:
            issues.append(f"🚨 Open CIDR detected: {cidr}")
    return issues

def check_instance_size(terraform_diff):
    issues = []
    if "instance_type" in terraform_diff:
        match = re.search(r'instance_type\s*=\s*"([^"]+)"', terraform_diff)
        if match:
            instance_type = match.group(1)
            if instance_type not in POLICIES["max_instance_types"]["allowed"]:
                issues.append(f"💰 Instance type `{instance_type}` may be costly")
    return issues
