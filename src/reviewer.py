import os
import subprocess
from rules import check_open_cidrs, check_instance_size
from ai_analyzer import analyze_with_ai
from github_client import post_pr_comment

def get_terraform_diff():
    base_sha = os.getenv("GITHUB_BASE_SHA")
    head_sha = os.getenv("GITHUB_SHA")

    try:
        if base_sha and head_sha:
            # PR context (best case)
            return subprocess.check_output(
                ["git", "diff", base_sha, head_sha]
            ).decode("utf-8")
        else:
            # Fallback: last commit
            return subprocess.check_output(
                ["git", "diff", "HEAD~1", "HEAD"]
            ).decode("utf-8")
    except subprocess.CalledProcessError:
        return ""

terraform_diff = get_terraform_diff()

issues = []
issues.extend(check_open_cidrs(terraform_diff))
issues.extend(check_instance_size(terraform_diff))

ai_feedback = analyze_with_ai(terraform_diff)

comment = "## 🤖 AI Terraform Review Report\n\n"

if not terraform_diff.strip():
    comment += "ℹ️ No Terraform changes detected.\n"
elif issues:
    comment += "### 🚦 Policy Violations\n"
    comment += "\n".join(issues) + "\n\n"
else:
    comment += "✅ No policy violations found.\n\n"

comment += "### 🧠 AI Analysis\n"
comment += ai_feedback

post_pr_comment(comment)
