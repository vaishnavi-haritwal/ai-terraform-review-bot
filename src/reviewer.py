import os
import subprocess
import traceback
from src.ai_analyzer import analyze_with_ai
from src.rules import check_open_cidrs, check_instance_size
from src.github_client import post_pr_comment

def get_terraform_diff():
    base_ref = os.getenv("GITHUB_BASE_REF")
    head_ref = os.getenv("GITHUB_HEAD_REF")

    # If we have base/head refs from the PR, attempt to fetch and diff them
    if base_ref and head_ref:
        try:
            # fetch the refs so origin/<ref> exists
            subprocess.check_call(["git", "fetch", "origin", base_ref, head_ref], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            diff = subprocess.check_output(["git", "diff", f"origin/{base_ref}...origin/{head_ref}"])
            return diff.decode("utf-8")
        except subprocess.CalledProcessError:
            # fallback below
            pass

    # Fallback: diff the last commit (works for single-commit PRs or local changes)
    try:
        diff = subprocess.check_output(["git", "diff", "HEAD~1..HEAD"])
        return diff.decode("utf-8")
    except subprocess.CalledProcessError:
        # Final fallback: list changed files or return helpful message
        try:
            names = subprocess.check_output(["git", "diff", "--name-only"])
            return names.decode("utf-8")
        except Exception as e:
            return f"Could not compute git diff: {e}"

def safe_analyze(terraform_diff):
    try:
        return analyze_with_ai(terraform_diff)
    except Exception as e:
        tb = traceback.format_exc()
        return f"AI analysis failed with error: {e}\n\nTraceback:\n{tb}"

def main():
    terraform_diff = get_terraform_diff()

    issues = []
    try:
        issues.extend(check_open_cidrs(terraform_diff))
        issues.extend(check_instance_size(terraform_diff))
    except Exception as e:
        issues.append(f"⚠️ Rule evaluation failed: {e}")

    ai_feedback = safe_analyze(terraform_diff)

    comment = "## 🤖 AI Terraform Review Report\n\n"

    if issues:
        comment += "### 🚦 Policy Violations\n"
        comment += "\n".join(issues) + "\n\n"
    else:
        comment += "✅ No policy violations found.\n\n"

    comment += "### 🧠 AI Analysis\n"
    comment += ai_feedback

    # Post comment; report error in output rather than crashing
    try:
        post_pr_comment(comment)
    except Exception as e:
        # Print to stdout/stderr so the workflow logs contain the details
        print("Failed to post PR comment:", e)
        print("Generated comment content:\n", comment)

if __name__ == "__main__":
    main()
