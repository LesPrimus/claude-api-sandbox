"""
Exercise: System Prompt
Use the system parameter to give Claude a persona or standing instructions.
"""

import asyncio

from anthropic import AsyncAnthropic
from anthropic.types import MessageParam, TextBlock
from dotenv import load_dotenv

load_dotenv()


async def main() -> str:
    messages: list[MessageParam] = [{"role": "user", "content": "Tell me a joke."}]

    async with AsyncAnthropic() as client:
        message = await client.messages.create(
            model="claude-haiku-4-5",
            system="You are a creative storyteller.",
            max_tokens=512,
            messages=messages,
            temperature=1,
        )

        return block.text if isinstance(block := message.content[0], TextBlock) else ""


if __name__ == "__main__":
    res = asyncio.run(main())
    print(res)
