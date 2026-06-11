# Project 4 — Structured Extractor

Turn messy free text (an email, a chat message, a form dump) into a **validated
Pydantic object**. Instead of parsing Claude's prose yourself, use structured
outputs: `client.messages.parse(...)` constrains the response to your schema and
hands you back a typed instance.

## Exercises

- Structured outputs (`output_config.format` under the hood)
- `client.messages.parse()` with a Pydantic model
- `response.parsed_output`

## What to build

Create `projects/extractor/extractor.py` with a model and a function:

```python
from pydantic import BaseModel


class Contact(BaseModel):
    name: str
    email: str
    interests: list[str]


def extract(client, text: str, *, model: str = "claude-opus-4-8") -> Contact:
    """Extract a Contact from free text using structured outputs."""
```

### Contract

- Define `Contact` exactly as above (the tests import it).
- `extract` must call `client.messages.parse(...)` passing your `Contact` model as
  the `output_format` argument, with a `messages` list containing the `text`.
- Return `response.parsed_output` (a validated `Contact`).

> The tests mock `client.messages.parse` to return a response whose
> `.parsed_output` is a `Contact`, and assert you returned it and that you passed
> `output_format=Contact`.

## Run the tests

```bash
uv run pytest projects/extractor/ -v
```

## Stretch goals

- Add optional fields (`phone: str | None = None`) and a nested model.
- Handle `response.stop_reason == "refusal"` (parsed_output may be absent).
- Extract a `list[Contact]` from a document containing several people.