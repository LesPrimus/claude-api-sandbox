"""
Exercise: Tool Use — @beta_tool decorator + tool runner
Define a tool with @beta_tool, pass it to tool_runner, and let the SDK
handle the agentic loop automatically.
"""

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

# TODO: define a tool with @beta_tool, wire it into tool_runner, print results


if __name__ == "__main__":
    pass
