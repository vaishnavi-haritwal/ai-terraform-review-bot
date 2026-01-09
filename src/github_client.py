from github import Github
import os

def _get_pr_number_from_ref(ref: str):
    # Expecting refs/pull/<pr_number>/merge
    if not ref:
        return None
    parts = ref.split("/")
    if len(parts) >= 3 and parts[0] == "refs" and parts[1] == "pull" and parts[2].isdigit():
        return int(parts[2])
    # last-segment numeric fallback
    last = parts[-1]
    if last.isdigit():
        return int(last)
    return None

def get_pr_number():
    # Try common sources for PR number
    ref = os.getenv("GITHUB_REF", "")
    pr = _get_pr_number_from_ref(ref)
    if pr:
        return pr

    # Some workflows/platforms set other envs -- try a few fallbacks
    for k in ("PR_NUMBER", "GITHUB_PR_NUMBER", "INPUT_PR_NUMBER"):
        val = os.getenv(k)
        if val and val.isdigit():
            return int(val)

    # Last-resort: try HEAD_REF for numeric (rare)
    head = os.getenv("GITHUB_HEAD_REF", "")
    if head and head.isdigit():
        return int(head)

    raise RuntimeError(f"Unable to determine PR number from environment (GITHUB_REF='{ref}')")

def post_pr_comment(message: str):
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    if not token:
        raise RuntimeError("Missing GITHUB_TOKEN environment variable")
    if not repo_name:
        raise RuntimeError("Missing GITHUB_REPOSITORY environment variable")

    pr_number = get_pr_number()
    github = Github(token)
    repo = github.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(message)
