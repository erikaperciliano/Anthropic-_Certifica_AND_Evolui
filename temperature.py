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

def chat(messages, system=None, temperature=1.0):

    params = {
        "model": "claude-sonnet-4-5",
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature
    }

    if system:
        params["system"] = system

    message = client.messages.create(**params)

    return message.content[0].text

add_user_message(
    messages,
    "Generate a one sentence movie idea."
)

answer = chat(
    messages,
    temperature=1.0
)

print(answer)