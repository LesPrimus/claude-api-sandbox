"""
Exercise: Token Counting
Use client.messages.count_tokens() to estimate cost before sending a request,
then compare with actual usage from the response.
"""

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

# TODO: count tokens on a prompt, then send it and compare with actual usage


if __name__ == "__main__":
    pass
