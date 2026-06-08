"""
Exercise: Async — Basic
Use AsyncAnthropic to send a message asynchronously with asyncio.
"""

import asyncio

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()

client = AsyncAnthropic()

# TODO: define an async main(), send a message, print the response


async def main():
    pass


if __name__ == "__main__":
    asyncio.run(main())
