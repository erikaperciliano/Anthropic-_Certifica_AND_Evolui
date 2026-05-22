from dotenv import load_dotenv
from anthropic import Anthropic
import json
import anthropic
import os

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

model = "claude-3-5-haiku-latest"

from statistics import mean

def run_evaluation(dataset, run_prompt_function):

    results = []

    for test_case in dataset:

        output = run_prompt_function(test_case)

        score = grade_output(
            test_case,
            output
        )

        results.append({
            "input": test_case,
            "output": output,
            "score": score
        })

    avg = mean([r["score"] for r in results])

    return {
        "average_score": avg,
        "results": results
    }
    
def grade_output(test_case, output):

    prompt = f"""
Task:
{test_case}

Output:
{output}

Grade this from 1-10.
Respond ONLY with a number.
"""

    response = client.messages.create(
        model=model,
        max_tokens=10,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return int(response.content[0].text.strip())