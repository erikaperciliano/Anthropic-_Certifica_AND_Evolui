import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

messages = []

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

model = "claude-sonnet-4-5"

def add_user_message(messages, text):
    user_message = {
        "role": "user",
        "content": text
    }

    messages.append(user_message)

def add_assistant_message(messages, text):
    assistant_message = {
        "role": "assistant",
        "content": text
    }

    messages.append(assistant_message)

def chat(messages, system=None, temperature=1.0, stop_sequences=None):

    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature
    }

    if system:
        params["system"] = system

    if stop_sequences:
        params["stop_sequences"] = stop_sequences

    response = client.messages.create(**params)

    return response.content[0].text

def generate_dataset():

    prompt = """
Generate an evaluation dataset for a prompt evaluation.

The dataset will be used to evaluate prompts that generate Python,
JSON, or Regex specifically for AWS-related tasks.

Generate an array of JSON objects.

Example output:

[
  {
    "task": "Description of task"
  }
]

Please generate 3 objects.
"""

    add_user_message(messages, prompt)

    add_assistant_message(messages, "[")

    text = chat(
        messages,
        stop_sequences=["```"]
    )

    json_text = "[" + text

    return json.loads(json_text)

dataset = generate_dataset()

print(dataset)

with open("dataset.json", "w") as f:
    json.dump(dataset, f, indent=2)