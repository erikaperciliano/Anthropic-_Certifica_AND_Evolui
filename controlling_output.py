import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

messages = []

prompt = """
Generate three different sample AWS CLI commands.
Each should be very short.
There should be no explanations.
"""

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

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

add_user_message(messages, prompt)

# Prefill
add_assistant_message(
    messages,
    "```bash\naws"
)

def chat(messages):

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=100,
        messages=messages,
        stop_sequences=["```"]
    )

    return "```bash\naws" + message.content[0].text

text = chat(messages)

print(text.strip())