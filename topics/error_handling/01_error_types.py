"""
Exercise: Error Handling
Catch typed SDK exceptions (BadRequestError, RateLimitError, etc.)
and inspect status codes and messages.
"""

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

# TODO: deliberately trigger different error types and handle them gracefully


if __name__ == "__main__":
    pass
