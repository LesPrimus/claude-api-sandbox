"""
Exercise: Streaming
Use the messages.stream() helper and iterate over text_stream.
"""
import asyncio
import sys

from anthropic import AsyncAnthropic
from anthropic.types import MessageParam
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

    messages: list[MessageParam] = [
        {
            "role": "user",
            "content": f"Summarize the contents of this website ({url}):\n\n{content}",
        }
    ]

    # messages.stream() is the high-level helper: it accumulates state and
    # exposes text_stream (text deltas only) plus get_final_message().
    async with AsyncAnthropic() as client, client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            print(text, end="", flush=True)
    print()


async def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.anthropic.com"
    await get_summary(url)


if __name__ == "__main__":
    asyncio.run(main())