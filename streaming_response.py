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

model = "claude-sonnet-4-5"

add_user_message(messages, "Write a 1 sentence description of a fake database")

with client.messages.stream(
    model=model,
    max_tokens=1000,
    messages=messages,
) as stream:
    
    for text in stream.text_stream:
        # Send each chunk to your client
        pass
    
        # Get the complete message for database storage
        final_message = stream.get_final_message()
