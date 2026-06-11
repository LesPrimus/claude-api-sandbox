# Project 1 — CLI Chatbot

Build a chatbot that holds a back-and-forth conversation, remembering everything
said so far. The Claude API is stateless: it has no memory between requests, so
*you* keep the running transcript and resend it every turn.

## Exercises

- Basic messages (`client.messages.create`)
- System prompts (giving Claude a persona)
- Multi-turn conversations (resending history)

## What to build

Create `projects/cli_chatbot/chatbot.py` with a `Conversation` class:

```python
class Conversation:
    def __init__(
        self,
        client=None,
        *,
        model: str = "claude-opus-4-8",
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> None:
        ...

    history: list[dict]            # the running transcript, starts empty

    def send(self, user_message: str) -> str:
        ...
```

### Contract

- `history` starts as an empty list and is a list of message dicts
  (`{"role": "user" | "assistant", "content": str}`).
- `send(user_message)` must:
  1. Append `{"role": "user", "content": user_message}` to `history`.
  2. Call `client.messages.create(model=..., max_tokens=..., messages=self.history)`,
     forwarding `system` when it was provided.
  3. Extract the text of the first `text` content block from the response.
  4. Append `{"role": "assistant", "content": <that text>}` to `history`.
  5. Return the assistant text.
- Because history is resent each turn, the second `send` call must include the
  first turn's user **and** assistant messages.
- When `system` is `None`, don't force a `system` argument (use
  `anthropic.NOT_GIVEN`, or omit it). When it's set, pass it through.

> Tip: `client` defaults to `None` so tests can inject a mock. In your
> `__main__` block, create a real one: `Conversation(Anthropic(), system="...")`.

## Run the tests

```bash
uv run pytest projects/cli_chatbot/ -v
```

## Stretch goals

- A real REPL loop in `__main__` reading from `input()`.
- Stream the reply with `client.messages.stream()` instead of blocking.
- Trim old turns once `client.messages.count_tokens(...)` crosses a budget.