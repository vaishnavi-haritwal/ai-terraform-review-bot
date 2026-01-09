import os
import subprocess
from src.ai_analyzer import analyze_with_ai
from src.rules import check_open_cidrs, check_instance_size
from src.github_client import post_pr_comment

def get_terraform_diff():
    try:
        # List changed Terraform files
        changed_files = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD"]
        ).decode("utf-8").splitlines()

        tf_files = [f for f in changed_files if f.endswith(".tf")]

        diff_content = ""
        for tf in tf_files:
            diff_content += subprocess.check_output(
                ["git", "diff", "HEAD", "--", tf]
            ).decode("utf-8")

        return diff_content
    except Exception:
        return ""

terraform_diff = get_terraform_diff()

issues = []
issues.extend(check_open_cidrs(terraform_diff))
issues.extend(check_instance_size(terraform_diff))

ai_feedback = analyze_with_ai(terraform_diff)

comment = "## 🤖 AI Terraform Review Report\n\n"

if not terraform_diff.strip():
    comment += "ℹ️ No Terraform changes detected.\n\n"
elif issues:
    comment += "### 🚦 Policy Violations\n"
    comment += "\n".join(issues) + "\n\n"
else:
    comment += "✅ No policy violations found.\n\n"

comment += "### 🧠 AI Analysis\n"
comment += ai_feedback

post_pr_comment(comment)
