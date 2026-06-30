"""
Exercise: Low-level Streaming
Use stream=True and iterate over raw SSE events.
"""
import asyncio
import sys

from anthropic import AsyncAnthropic
from anthropic.types import MessageParam, RawContentBlockDeltaEvent, TextDelta
from dotenv import load_dotenv
import httpx

load_dotenv()

SYSTEM_PROMPT = """
You are a snarky assistant that analyzes the contents of a website,
and provides a short, snarky, humorous summary, ignoring text that might be navigation related.
Respond in markdown. Do not wrap the markdown in a code block - respond just with the markdown.
"""


async def get_content(url: str) -> str:
    """Fetch the raw text/HTML of a web page."""
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; claude-summarizer/1.0)"},
        )
        response.raise_for_status()
        return response.text


async def get_summary(url: str) -> None:
    """Fetch a page and stream a snarky summary from Claude."""
    content = await get_content(url)

    client = AsyncAnthropic()

    messages: list[MessageParam] = [
        {
            "role": "user",
            "content": f"Summarize the contents of this website ({url}):\n\n{content}",
        }
    ]

    # stream=True returns an AsyncStream of raw SSE events (no accumulation).
    stream = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
        stream=True,
    )

    async for event in stream:
        if isinstance(event, RawContentBlockDeltaEvent) and isinstance(event.delta, TextDelta):
            print(event.delta.text, end="", flush=True)
    print()


async def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.anthropic.com"
    await get_summary(url)


if __name__ == "__main__":
    asyncio.run(main())