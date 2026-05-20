import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

messages = []

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

def add_user_message(messages, text):
    user_message = {
        "role": "user",
        "content": text
    }
    messages.append(user_message)

def chat(messages, system=None):
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system=system,
        messages=messages,
    )
    return message.content[0].text

add_user_message(
    messages,
    "Write a Python function that checks a string for duplicate characters."
)

answer = chat(
    messages,
    system="You are a Python engineer who writes very concise code"
)

print(answer)