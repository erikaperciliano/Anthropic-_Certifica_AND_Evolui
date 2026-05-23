import os
import json
from datetime import datetime, timedelta

from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import Message, ToolParam

# ==========================================
# ENV + CLIENT
# ==========================================

load_dotenv()

client = Anthropic()

model = "claude-sonnet-4-5"

# ==========================================
# MESSAGE HELPERS
# ==========================================

def add_user_message(messages, message):

    if isinstance(message, list):

        user_message = {
            "role": "user",
            "content": message
        }

    else:

        user_message = {
            "role": "user",
            "content": (
                message.content
                if isinstance(message, Message)
                else message
            ),
        }

    messages.append(user_message)

def add_assistant_message(messages, message):

    assistant_message = {
        "role": "assistant",
        "content": (
            message.content
            if isinstance(message, Message)
            else message
        ),
    }

    messages.append(assistant_message)

# ==========================================
# CHAT
# ==========================================

def chat(
    messages,
    system=None,
    temperature=1.0,
    stop_sequences=None,
    tools=None
):

    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature,
    }

    if stop_sequences:
        params["stop_sequences"] = stop_sequences

    if tools:
        params["tools"] = tools

    if system:
        params["system"] = system

    response = client.messages.create(**params)

    return response


def text_from_message(message):

    return "\n".join([
        block.text
        for block in message.content
        if block.type == "text"
    ])

# ==========================================
# TOOLS
# ==========================================

def get_current_datetime(
    date_format="%Y-%m-%d %H:%M:%S"
):

    if not date_format:
        raise ValueError(
            "date_format cannot be empty"
        )

    return datetime.now().strftime(date_format)


def add_duration_to_datetime(
    datetime_str,
    duration=0,
    unit="days",
    input_format="%Y-%m-%d"
):

    date = datetime.strptime(
        datetime_str,
        input_format
    )

    if unit == "seconds":
        new_date = date + timedelta(
            seconds=duration
        )

    elif unit == "minutes":
        new_date = date + timedelta(
            minutes=duration
        )

    elif unit == "hours":
        new_date = date + timedelta(
            hours=duration
        )

    elif unit == "days":
        new_date = date + timedelta(
            days=duration
        )

    elif unit == "weeks":
        new_date = date + timedelta(
            weeks=duration
        )

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

    return new_date.strftime(
        "%A, %B %d, %Y %I:%M:%S %p"
    )


def set_reminder(content, timestamp):

    print(
        f"\n----\n"
        f"Setting reminder for {timestamp}:\n"
        f"{content}\n"
        f"----\n"
    )

    return {
        "success": True,
        "message": (
            f"Reminder set for {timestamp}"
        )
    }

# ==========================================
# TOOL SCHEMAS
# ==========================================

get_current_datetime_schema = ToolParam(
    {
        "name": "get_current_datetime",
        "description": (
            "Get the current datetime"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "date_format": {
                    "type": "string",
                    "default": (
                        "%Y-%m-%d %H:%M:%S"
                    )
                }
            },
            "required": []
        }
    }
)

add_duration_to_datetime_schema = ToolParam(
    {
        "name": "add_duration_to_datetime",
        "description": (
            "Add a duration to a datetime"
        ),
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
            "required": [
                "datetime_str"
            ]
        }
    }
)

set_reminder_schema = ToolParam(
    {
        "name": "set_reminder",
        "description": (
            "Create a reminder"
        ),
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
)

batch_tool_schema = ToolParam(
    {
        "name": "batch_tool",
        "description": (
            "Invoke multiple tools"
        ),
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

            "required": [
                "invocations"
            ]
        }
    }
)

# ==========================================
# TOOL EXECUTION
# ==========================================

def run_tool(tool_name, tool_input):

    if tool_name == "get_current_datetime":

        return get_current_datetime(
            **tool_input
        )

    elif tool_name == (
        "add_duration_to_datetime"
    ):

        return add_duration_to_datetime(
            **tool_input
        )

    elif tool_name == "set_reminder":

        return set_reminder(
            **tool_input
        )

    elif tool_name == "batch_tool":

        results = []

        for invocation in tool_input[
            "invocations"
        ]:

            result = run_tool(
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

# ==========================================
# RUN TOOL CALLS
# ==========================================

def run_tools(message):

    tool_requests = [

        block

        for block in message.content

        if block.type == "tool_use"
    ]

    tool_result_blocks = []

    for tool_request in tool_requests:

        try:

            tool_output = run_tool(
                tool_request.name,
                tool_request.input
            )

            tool_result_block = {
                "type": "tool_result",
                "tool_use_id": (
                    tool_request.id
                ),
                "content": json.dumps(
                    tool_output
                ),
                "is_error": False,
            }

        except Exception as e:

            tool_result_block = {
                "type": "tool_result",
                "tool_use_id": (
                    tool_request.id
                ),
                "content": f"Error: {e}",
                "is_error": True,
            }

        tool_result_blocks.append(
            tool_result_block
        )

    return tool_result_blocks

# ==========================================
# CONVERSATION LOOP
# ==========================================

def run_conversation(messages):

    tools = [

        get_current_datetime_schema,

        add_duration_to_datetime_schema,

        set_reminder_schema,

        batch_tool_schema
    ]

    while True:

        response = chat(
            messages,
            tools=tools
        )

        add_assistant_message(
            messages,
            response
        )

        text_output = text_from_message(
            response
        )

        if text_output:
            print(
                "\nAssistant:\n"
            )
            print(text_output)

        if response.stop_reason != "tool_use":
            break

        tool_results = run_tools(
            response
        )

        add_user_message(
            messages,
            tool_results
        )

    return messages

# ==========================================
# TEST
# ==========================================

messages = []

add_user_message(
    messages,
    (
        "Remind me in 3 days "
        "to pay my electricity bill"
    )
)

run_conversation(messages)