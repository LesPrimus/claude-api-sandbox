"""
Exercise: Tool Use — Manual agentic loop
Define tools as raw JSON schemas and drive the tool-call / tool-result
cycle manually, giving you full control over each iteration.
"""

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

# TODO: define tools as dicts, loop until stop_reason == "end_turn",
#       execute tool calls and feed results back as tool_result blocks


if __name__ == "__main__":
    pass
