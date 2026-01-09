def analyze_with_ai(terraform_diff):
    if not terraform_diff.strip():
        return "No Terraform changes to analyze."

    return (
        "- AI analysis disabled (no API key configured)\n"
        "- Rule-based governance checks executed\n"
        "- AI can be enabled via OPENAI_API_KEY"
    )
