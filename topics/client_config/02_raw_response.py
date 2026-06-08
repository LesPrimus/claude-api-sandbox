"""
Exercise: Raw Response & Request ID
Use with_raw_response to access HTTP headers (request-id, rate-limit headers)
before parsing the response body.
"""

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

# TODO: call with_raw_response, print headers, then parse and print content


if __name__ == "__main__":
    pass
