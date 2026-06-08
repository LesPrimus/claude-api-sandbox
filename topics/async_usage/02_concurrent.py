"""
Exercise: Async — Concurrent requests
Use asyncio.gather() to fire multiple requests in parallel and compare
wall-clock time against sequential execution.
"""

import asyncio

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()

client = AsyncAnthropic()

# TODO: run N requests concurrently with asyncio.gather(),
#       measure and print elapsed time vs sequential estimate


async def main():
    pass


if __name__ == "__main__":
    asyncio.run(main())
