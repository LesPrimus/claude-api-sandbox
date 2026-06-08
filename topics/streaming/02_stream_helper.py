"""
Exercise: Streaming Helper
Use the client.messages.stream() context manager and text_stream iterator.
Also explore get_final_message() for usage stats after streaming.
"""

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

# TODO: stream with messages.stream(), print tokens as they arrive,
#       then print total usage from get_final_message()


if __name__ == "__main__":
    pass
