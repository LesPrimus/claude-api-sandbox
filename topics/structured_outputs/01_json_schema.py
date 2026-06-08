"""
Exercise: Structured Outputs — JSON Schema
Use output_config.format with a json_schema to guarantee
valid, parseable JSON in the response.
"""

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

# TODO: define a JSON schema, send a request with output_config,
#       parse and pretty-print the structured response


if __name__ == "__main__":
    pass
