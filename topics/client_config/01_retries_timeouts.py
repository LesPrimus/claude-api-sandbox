"""
Exercise: Client Config — Retries & Timeouts
Configure max_retries and timeout at the client level and per-request
using with_options().
"""

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

# TODO: show client-level config, then per-request override with with_options()


if __name__ == "__main__":
    pass
