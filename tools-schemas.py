from datetime import datetime

from dotenv import load_dotenv
from anthropic import Anthropic
import anthropic
import os
import json

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

model = "claude-sonnet-4-5"

def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)


get_current_datetime_schema = {
    "name": "get_current_datetime",
    "description": "Returns the current date and time formatted according to the specified format",
    "input_schema": {
        "type": "object",
        "properties": {
            "date_format": {
                "type": "string",
                "description": "A string specifying the format of the returned datetime. Uses Python's strftime format codes.",
                "default": "%Y-%m-%d %H:%M:%S"
            }
        },
        "required": []
    }
}

messages = [
    {
        "role": "user",
        "content": "What time is it right now?"
    }
]

response = client.messages.create(
    model = model,
    max_tokens = 300,
    messages = messages,
    tools = [get_current_datetime_schema]
)

print("\nMODEL RESPONSE: ")
print(response)

# Detect tool use
tool_use = next(
    (block for block in response.content if block.type == "tool_use"),
    None
)

if tool_use:
    
    print("\nTOOL CALL:")
    print(tool_use.name)
    print(tool_use.input)
    
    tool_result = get_current_datetime(
        **tool_use.input
    )
    
    print("\nTOOL RESULT:")
    print(tool_result)