import os
import json
from statistics import mean
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

model = "claude-sonnet-4-5"

def add_user_message(messages, text):
    messages.append({
        "role": "user",
        "content": text
    })

def add_assistant_message(messages, text):
    messages.append({
        "role": "assistant",
        "content": text
    })

def chat(messages, stop_sequences=None):

    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages
    }

    if stop_sequences:
        params["stop_sequences"] = stop_sequences

    response = client.messages.create(**params)

    return response.content[0].text

def run_prompt(test_case):

    prompt = f"""
Write a Python solution for this task:

{test_case["task"]}
"""

    messages = []

    add_user_message(messages, prompt)

    response = chat(messages)

    return response

def grade_by_model(test_case, output):

    eval_prompt = f"""
You are an expert code reviewer.

Evaluate this AI-generated solution.

Task:
{test_case["task"]}

Solution:
{output}

Provide your evaluation as JSON with:
- strengths
- weaknesses
- reasoning
- score
"""

    messages = []

    add_user_message(messages, eval_prompt)

    add_assistant_message(messages, "{")

    eval_text = chat(
        messages,
        stop_sequences=["```"]
    )

    json_text = "{" + eval_text

    return json.loads(json_text)

def run_test_case(test_case):

    output = run_prompt(test_case)

    model_grade = grade_by_model(test_case, output)

    score = model_grade["score"]
    reasoning = model_grade["reasoning"]

    return {
        "output": output,
        "test_case": test_case,
        "score": score,
        "reasoning": reasoning
    }

def run_eval(dataset):

    results = []

    for test_case in dataset:
        result = run_test_case(test_case)
        results.append(result)

    average_score = mean(
        [result["score"] for result in results]
    )

    print(f"Average score: {average_score}")

    return results