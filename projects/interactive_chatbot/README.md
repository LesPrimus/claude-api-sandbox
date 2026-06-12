# Project 7 — Interactive Streaming Chatbot

Project 1 built a `Conversation` that remembers history. This project takes the
three stretch goals listed at the bottom of that project and turns each into a
graded exercise:

1. A real REPL loop in `__main__` reading from `input()`.
2. Stream the reply with `client.messages.stream()` instead of blocking.
3. Trim old turns once `client.messages.count_tokens(...)` crosses a budget.

Each exercise is independent — its own solution file and test file — so you can
do them in any order. None of them call the network; the tests inject mocks.

## Exercises

- Streaming (`client.messages.stream()`, `text_stream`, `get_final_message()`)
- Token counting (`client.messages.count_tokens()`)
- Driving an interactive loop and keeping a transcript inside a token budget

---

## Exercise 1 — REPL loop (`repl.py`)

A chat program is a loop: read a line, send it, print the reply, repeat. Pull
that loop out of `__main__` into a testable function so the I/O can be mocked.

```python
def run_repl(
    conversation,
    *,
    input_fn=input,
    output_fn=print,
    prompt="you> ",
) -> int:
    ...
```

### Contract

- `conversation` is any object with a `send(text: str) -> str` method (in real
  use, a Project 1 `Conversation`; in tests, a mock).
- Loop forever: call `input_fn(prompt)` to read one line.
- Stop the loop when the user types `exit` or `quit` (case-insensitive, after
  stripping surrounding whitespace), **or** when `input_fn` raises `EOFError`
  (Ctrl-D) or `KeyboardInterrupt` (Ctrl-C). These end the session cleanly — do
  not re-raise.
- A blank or whitespace-only line is ignored: do **not** call
  `conversation.send` for it, just loop again.
- For any other line, call `conversation.send(line)` and pass the returned text
  to `output_fn`.
- Return the number of messages actually sent to `conversation` (so a session
  with two real prompts returns `2`).
- Default `input_fn`/`output_fn` to the builtins so `__main__` can call
  `run_repl(Conversation(Anthropic()))` with no arguments.

---

## Exercise 2 — Streaming replies (`streaming.py`)

Blocking `create()` waits for the whole reply before you see anything.
`stream()` yields text as it is generated. Build a `StreamingConversation` whose
`send` streams.

```python
class StreamingConversation:
    def __init__(self, client, *, model="claude-haiku-4-5",
                 system=None, max_tokens=1024) -> None:
        ...

    history: list[dict]   # same shape as Project 1, starts empty

    def send(self, user_message: str, on_text=None) -> str:
        ...
```

### Contract

- `history` starts empty and holds `{"role": ..., "content": ...}` dicts, exactly
  like Project 1.
- `send` must:
  1. Append `{"role": "user", "content": user_message}` to `history`.
  2. Open the streaming context manager:
     `with client.messages.stream(model=..., max_tokens=..., messages=self.history, system=...) as stream:`
     (forward `system` only when it was provided).
  3. Iterate `stream.text_stream`, concatenating each chunk into the full reply.
  4. If `on_text` is given, call `on_text(chunk)` for every chunk as it arrives
     (this is what lets a caller print tokens live).
  5. Append `{"role": "assistant", "content": <full reply>}` to `history`.
  6. Return the full reply text.
- The reply is the chunks joined in order, with nothing added between them.

> Tip: after the loop you can call `stream.get_final_message()` for usage stats,
> but the graded text comes from `text_stream`.

---

## Exercise 3 — Trim to a token budget (`trimming.py`)

History grows every turn, and you pay for all of it on every request. Before
sending, drop the oldest turns until the transcript fits a token budget. Write a
pure function:

```python
def trim_to_budget(
    client,
    messages: list[dict],
    *,
    model: str,
    budget: int,
    system=None,
) -> list[dict]:
    ...
```

### Contract

- Ask the API how big the transcript is with
  `client.messages.count_tokens(model=model, messages=<candidate>, system=...)`
  (forward `system` only when provided). The result has an `.input_tokens`
  attribute.
- If the current `messages` already counts at or under `budget`, return it
  unchanged.
- While it is over budget, drop the **oldest turn** — the first two messages
  (a user message and its assistant reply) — then count again.
- Stop dropping once the count is within budget **or** only one turn (two
  messages) is left. The most recent turn must always survive, even if it alone
  exceeds the budget — never loop forever and never return an empty list.
- Do not mutate the caller's list; return a new (possibly shorter) list.

> Why drop a pair at a time? Removing whole user+assistant turns keeps the
> transcript starting on a `user` message, which the API requires.

---

## Run the tests

```bash
uv run pytest projects/interactive_chatbot/ -v
```

## Stretch goals

- Combine all three: a `StreamingConversation` whose `send` calls
  `trim_to_budget` before streaming, driven by `run_repl` in `__main__`.
- Show a live spinner or `█` cursor while streaming, cleared when done.
- Print `get_final_message().usage` after each reply so you watch the cost grow.