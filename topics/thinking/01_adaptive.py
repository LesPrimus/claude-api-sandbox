"""
Exercise: Adaptive Thinking
Enable thinking={"type": "adaptive"} and inspect thinking blocks
alongside the final text response.
"""

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

# TODO: send a request with adaptive thinking enabled,
#       iterate content blocks and print thinking vs text separately


if __name__ == "__main__":
    pass
