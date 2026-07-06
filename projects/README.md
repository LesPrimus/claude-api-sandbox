# Build Projects

Where `topics/` teaches one API method at a time, each project here asks you to
**build a small working thing** that composes several features together.

Every project folder contains exactly two files:

- `README.md` — the brief: what to build, which API features it exercises, and
  the exact contract your solution module must satisfy.
- `test_<name>.py` — a fully-mocked pytest suite (no real API calls, no API key
  needed) that grades your implementation.

You write the third file — the solution module named in the README. Until it
exists the tests fail with a "not implemented yet" message; once your
implementation matches the contract, they pass.

Run one project's tests:

```bash
uv run pytest projects/cli_chatbot/ -v
```

Run them all:

```bash
uv run pytest projects/ -v
```

All solution modules take an injected `client` (the Anthropic SDK client) so the
tests can pass a mock. In real use your `if __name__ == "__main__":` block builds
a real `Anthropic()` — but the graded functions never construct one themselves.

| # | Project | Build | Exercises |
|---|---------|-------|-----------|
| 1 | `cli_chatbot` | A multi-turn chatbot that keeps conversation history | basic messages, system prompts, multi-turn |
| 2 | `doc_qa` | Upload a document once, ask many questions about it | Files API, document blocks |
| 3 | `tool_agent` | An agent that calls local functions in a manual loop | tool use, agentic loop, tool results |
| 4 | `extractor` | Turn messy text into validated Pydantic objects | structured outputs, `messages.parse()` |
| 5 | `batch_classifier` | Classify a list of items via the Batches API | batches, polling, result parsing |
| 6 | `coding_assistant` | A file-editing agent with a human approval gate | adaptive thinking, tool use, safety |
| 7 | `interactive_chatbot` | Project 1's chatbot, made live: REPL loop, streaming, budget trimming | streaming, token counting, interactive loop |
| 8 | `brochure_generator` | Scrape a site's links, pick the relevant ones, stream a brochure | async scraping, structured outputs, streaming |

Suggested order: 1 → 4 → 3 → 2 → 5 → 6 → 7 (roughly easiest to hardest).

> Project 7 picks up the three stretch goals from Project 1 and grades them.