import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_with_ai(terraform_diff):
    prompt = f"""You are a senior DevOps engineer.
Review the following Terraform changes and identify:
1. Security risks
2. Cost inefficiencies
3. Best practice violations

Terraform diff:
{terraform_diff}
Respond in bullet points.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message["content"]
