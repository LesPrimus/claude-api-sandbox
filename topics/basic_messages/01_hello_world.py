"""
Exercise: Hello World
Send a basic message and inspect the response object.
"""

from anthropic import AsyncAnthropic
from anthropic.types import MessageParam
from dotenv import load_dotenv
import asyncio
from dataclasses import dataclass

load_dotenv()


@dataclass(frozen=True)
class Response:
    text: str
    input_tokens: int
    output_tokens: int


client = AsyncAnthropic()


async def main() -> Response:
    messages: list[MessageParam] = [
        {
            "role": "user",
            "content": "Hello, Claude!",
        }
    ]
    message = await client.messages.create(
        max_tokens=1024,
        messages=messages,
        model="claude-opus-4-8",
    )

    [content] = message.content
    return Response(
        text=content.text,
        input_tokens=message.usage.input_tokens,
        output_tokens=message.usage.output_tokens,
    )


if __name__ == "__main__":
    response = asyncio.run(main())
    print(response)
