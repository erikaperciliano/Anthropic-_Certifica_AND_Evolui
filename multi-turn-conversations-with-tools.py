import os
import json
from datetime import datetime, timedelta

from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

model = "claude-sonnet-4-5"

# =========================
# TOOLS
# =========================

def add_duration_to_datetime(
    datetime_str,
    duration=0,
    unit="days",
    input_format="%Y-%m-%d"
):

    date = datetime.strptime(datetime_str, input_format)

    if unit == "seconds":
        new_date = date + timedelta(seconds=duration)

    elif unit == "minutes":
        new_date = date + timedelta(minutes=duration)

    elif unit == "hours":
        new_date = date + timedelta(hours=duration)

    elif unit == "days":
        new_date = date + timedelta(days=duration)

    elif unit == "weeks":
        new_date = date + timedelta(weeks=duration)

    elif unit == "months":

        month = date.month + duration
        year = date.year + month // 12
        month = month % 12

        if month == 0:
            month = 12
            year -= 1

        day = min(
            date.day,
            [
                31,
                29 if year % 4 == 0 and (
                    year % 100 != 0 or year % 400 == 0
                ) else 28,
                31,
                30,
                31,
                30,
                31,
                31,
                30,
                31,
                30,
                31,
            ][month - 1],
        )

        new_date = date.replace(
            year=year,
            month=month,
            day=day
        )

    elif unit == "years":

        try:
            new_date = date.replace(
                year=date.year + duration
            )

        except ValueError:
            new_date = date.replace(
                month=2,
                day=28,
                year=date.year + duration
            )

    else:
        raise ValueError(
            f"Unsupported time unit: {unit}"
        )

    return {
        "result": new_date.strftime(
            "%A, %B %d, %Y %I:%M:%S %p"
        )
    }


def set_reminder(content, timestamp):

    print(
        f"\n----\n"
        f"Setting reminder for {timestamp}:\n"
        f"{content}\n"
        f"----\n"
    )

    return {
        "success": True,
        "message": f"Reminder set for {timestamp}"
    }


# =========================
# SCHEMAS
# =========================

add_duration_to_datetime_schema = {
    "name": "add_duration_to_datetime",
    "description": "Add a duration to a datetime",
    "input_schema": {
        "type": "object",
        "properties": {
            "datetime_str": {
                "type": "string"
            },
            "duration": {
                "type": "number"
            },
            "unit": {
                "type": "string",
                "enum": [
                    "seconds",
                    "minutes",
                    "hours",
                    "days",
                    "weeks",
                    "months",
                    "years"
                ]
            },
            "input_format": {
                "type": "string"
            }
        },
        "required": ["datetime_str"]
    }
}

set_reminder_schema = {
    "name": "set_reminder",
    "description": "Create a reminder",
    "input_schema": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string"
            },
            "timestamp": {
                "type": "string"
            }
        },
        "required": [
            "content",
            "timestamp"
        ]
    }
}

batch_tool_schema = {
    "name": "batch_tool",
    "description": "Invoke multiple tools",
    "input_schema": {
        "type": "object",
        "properties": {
            "invocations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "arguments": {
                            "type": "object"
                        }
                    },
                    "required": [
                        "name",
                        "arguments"
                    ]
                }
            }
        },
        "required": ["invocations"]
    }
}

tools = [
    add_duration_to_datetime_schema,
    set_reminder_schema,
    batch_tool_schema
]

# =========================
# TOOL EXECUTION
# =========================

def execute_tool(tool_name, tool_input):

    if tool_name == "add_duration_to_datetime":
        return add_duration_to_datetime(
            **tool_input
        )

    elif tool_name == "set_reminder":
        return set_reminder(
            **tool_input
        )

    elif tool_name == "batch_tool":

        results = []

        for invocation in tool_input["invocations"]:

            result = execute_tool(
                invocation["name"],
                invocation["arguments"]
            )

            results.append({
                "tool": invocation["name"],
                "result": result
            })

        return results

    else:
        raise ValueError(
            f"Unknown tool: {tool_name}"
        )

# =========================
# CHAT LOOP
# =========================

messages = [
    {
        "role": "user",
        "content": (
            "Set a reminder 3 days from "
            "2025-06-01 saying "
            "'Pay electricity bill'"
        )
    }
]

response = client.messages.create(
    model=model,
    max_tokens=1000,
    messages=messages,
    tools=tools
)

print("\nMODEL RESPONSE:")
print(response)

# =========================
# HANDLE TOOL CALLS
# =========================

for block in response.content:

    if block.type == "tool_use":

        tool_name = block.name
        tool_input = block.input

        print("\nTOOL CALL:")
        print(tool_name)
        print(tool_input)

        result = execute_tool(
            tool_name,
            tool_input
        )

        print("\nTOOL RESULT:")
        print(result)