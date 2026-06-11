# Project 6 — Coding Assistant (with an approval gate)

Build a small agent that can read and write files inside a sandbox directory, on
Claude's instruction — but only after a **human approval gate** allows each
write, and only for paths that stay inside the sandbox. This combines adaptive
thinking, tool use, and the safety thinking that real coding agents need.

## Exercises

- Adaptive thinking (`thinking={"type": "adaptive"}`)
- Client-side tools the harness executes (`read_file`, `write_file`)
- Human-in-the-loop approval before side effects
- Path-traversal safety (refusing writes that escape the sandbox)

## What to build

Create `projects/coding_assistant/assistant.py`.

```python
def safe_path(workdir, relpath: str):
    """Resolve relpath under workdir; raise ValueError if it escapes."""

def run(
    client,
    prompt: str,
    *,
    workdir,
    model: str = "claude-opus-4-8",
    approve=lambda name, tool_input: True,
    max_steps: int = 10,
) -> str:
    """Agentic loop with read_file / write_file tools; return final text."""
```

### Contract

`safe_path(workdir, relpath)`:
- Return the resolved absolute path of `relpath` joined under `workdir`.
- Raise `ValueError` if the resolved path is **not** inside `workdir`
  (e.g. `"../secrets"` or an absolute path outside).

`run(...)`:
- Enable adaptive thinking: pass `thinking={"type": "adaptive"}` to
  `client.messages.create`.
- Offer two tools: `read_file(path)` and `write_file(path, content)`.
- Drive the manual loop (like Project 3). For each `tool_use` block:
  - `read_file`: read and return the file's text (via `safe_path`).
  - `write_file`: **first call `approve("write_file", tool_input)`**. If it
    returns `False`, return a `tool_result` with `"is_error": True` and do **not**
    write. If `True`, write the content (via `safe_path`) and return a success
    message.
- Always resolve paths through `safe_path`; a `ValueError` should come back as an
  error `tool_result`, not crash the loop.
- Stop when `stop_reason != "tool_use"` and return the first `text` block.

> The tests check: a write happens when approval is granted; the file is *not*
> written when approval is denied (and the loop still finishes); `approve` is
> called with the tool name and input; and `safe_path` rejects traversal.

## Run the tests

```bash
uv run pytest projects/coding_assistant/ -v
```

## Stretch goals

- Show summarized thinking (`thinking={"type": "adaptive", "display": "summarized"}`).
- Add an `edit_file` (string-replace) tool with a staleness check.
- Make `approve` an interactive `input("approve write? [y/N] ")` prompt.