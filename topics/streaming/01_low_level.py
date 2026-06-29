"""
Exercise: Low-level Streaming
Use stream=True and iterate over raw SSE events.
"""
import asyncio

from anthropic import Anthropic, AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()


async def main():

    client = AsyncAnthropic()

    async with client.messages.stream(
        model="claude-sonnet-4-6",
        messages=[{"role": "user", "content": "Tell me a joke."}],
        max_tokens=1024,
    ) as stream:
        async for text in stream.text_stream:
            print(text, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
