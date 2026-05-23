from datetime import datetime

from dotenv import load_dotenv
from anthropic import Anthropic
import anthropic
import os

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

model = "claude-3-5-haiku-latest"

def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)

print(get_current_datetime("%H:%M"))
# print(get_current_datetime(""))
