# Project 3 — Tool-Use Agent

Build an agent that gives Claude a real tool, then runs the **manual agentic
loop**: call the API, and while Claude asks to use a tool, execute it, feed the
result back, and call again — until Claude stops and gives a final answer.

## Exercises

- Tool definitions (JSON schema)
- The `tool_use` stop reason and `tool_use` content blocks
- Returning `tool_result` blocks with the matching `tool_use_id`
- Looping until `stop_reason == "end_turn"`

## What to build

Create `projects/tool_agent/agent.py`.

Give Claude a `multiply` tool. Define and export:

```python
TOOLS = [
    {
        "name": "multiply",
        "description": "Multiply two numbers and return the product.",
        "input_schema": {
            "type": "object",
            "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
            "required": ["a", "b"],
        },
    }
]


def execute_tool(name: str, tool_input: dict) -> str:
    """Run a tool by name; return its result as a string."""


def run(client, prompt: str, *, model: str = "claude-opus-4-8", max_steps: int = 10) -> str:
    """Drive the agentic loop and return Claude's final text answer."""
```

### Contract

`execute_tool`:
- For `name == "multiply"`, return `str(a * b)` from `tool_input`.

`run`:
- Start with `messages = [{"role": "user", "content": prompt}]`.
- Loop (bounded by `max_steps`):
  1. `response = client.messages.create(model=..., max_tokens=..., tools=TOOLS, messages=messages)`.
  2. If `response.stop_reason != "tool_use"`, return the first `text` block's text.
  3. Otherwise: append `{"role": "assistant", "content": response.content}`, then
     for every `tool_use` block, call `execute_tool(block.name, block.input)` and
     collect a result dict:
     `{"type": "tool_result", "tool_use_id": block.id, "content": <result>}`.
  4. Append `{"role": "user", "content": <list of tool_result dicts>}` and loop.

> The tests drive a two-step conversation: first the model asks to multiply
> 6 × 7, then (after you hand back `"42"`) it replies with the final answer.
> They assert the loop ran twice and that the `tool_result` you returned carried
> the matching `tool_use_id` and the computed value.

## Run the tests

```bash
uv run pytest projects/tool_agent/ -v
```

## Stretch goals

- Add more tools (a calculator that evaluates an expression, a clock, etc.).
- Rewrite it with the `@beta_tool` decorator + `client.beta.messages.tool_runner`
  and compare (this also completes `topics/tool_use/01_beta_tool_decorator.py`).
- Handle a tool that raises, returning `"is_error": True` in the tool_result.