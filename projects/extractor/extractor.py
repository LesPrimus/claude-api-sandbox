from anthropic import Anthropic
from anthropic.types import MessageParam
from dotenv import load_dotenv
from pydantic import BaseModel

from projects._models import ModelType

load_dotenv()


class Contact(BaseModel):
    name: str
    email: str
    interests: list[str]


def extract(
    client: Anthropic, text: str, *, model: str = ModelType.HAIKU
) -> Contact | None:
    """Extract a Contact from free text using structured outputs."""
    messages: list[MessageParam] = [{"role": "user", "content": text}]
    response = client.messages.parse(
        model=model,
        max_tokens=1024,
        messages=messages,
        output_format=Contact,
    )

    return response.parsed_output
