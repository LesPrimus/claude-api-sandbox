"""
Exercise: Hello World
Send a basic message and inspect the response object.
"""

from anthropic import Anthropic
from anthropic.types import MessageParam
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

messages: list[MessageParam] = [
    {
        "role": "user",
        "content": "Hello, Claude!",
    }
]


message = client.messages.create(
    max_tokens=1024,
    messages=messages,
    model="claude-opus-4-8",
)


if __name__ == "__main__":
    [content] = message.content
    print(content.text)
    print("Input tokens: ", message.usage.input_tokens)
    print("Output tokens: ", message.usage.output_tokens)
