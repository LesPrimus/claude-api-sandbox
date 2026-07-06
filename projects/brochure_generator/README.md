# Project 8 — Brochure Generator

Given a company URL, generate a short marketing **brochure** in markdown. This
composes three things you've practised separately:

- **async scraping** with `httpx.AsyncClient` + BeautifulSoup (as in
  `topics/streaming/01_low_level.py`),
- **structured outputs** via `client.messages.parse()` (as in
  `projects/extractor/`), and
- **streaming** via `client.messages.stream()` (as in
  `topics/streaming/02_stream_helper.py`).

It's async end to end: `AsyncAnthropic` for Claude and `asyncio.gather` to fetch
the selected pages concurrently.

## Pipeline

```
url ─▶ fetch_html ─▶ extract_links ─▶ [urls]
                                         │
                    select_relevant_links(client)   ← LLM call #1 (structured)
                                         │
                    RelevantLinks{links:[{type,url}]}
                                         │
          asyncio.gather(fetch_html) over the selected urls (concurrent)
                                         │
          extract_text per page → combined context
                                         │
                    build_brochure(client) ─▶ stream markdown  ← LLM call #2
```

Two LLM calls: **#1** picks the brochure-relevant links as a structured
`RelevantLinks`; **#2** streams the brochure. Scraping is one level deep
(landing page + each selected page) — no recursion.

## Exercises

- `httpx.AsyncClient` + BeautifulSoup scraping
- Structured outputs — `client.messages.parse(..., output_format=RelevantLinks)`
- Streaming — `async with client.messages.stream(...)` + `text_stream`
- `asyncio.gather(..., return_exceptions=True)` for concurrent, fault-tolerant
  fetches

## What it builds — `brochure.py`

The structured "relevant links in a structured format":

```python
class Link(BaseModel):
    type: str   # "about page", "careers page", "products", ...
    url: str

class RelevantLinks(BaseModel):
    links: list[Link]
```

Functions (all take an injected `client`; network lives behind an injectable
`fetch_html`, so the tests are fully offline):

- `async fetch_html(url) -> str` — raw HTML for a URL.
- `extract_links(html, base_url) -> list[str]` — **pure**: absolute http(s)
  links, relative resolution, deduped, dropping `mailto:`/`tel:`/`#`.
- `extract_text(html) -> str` — **pure**: visible text, scripts/styles removed.
- `async select_relevant_links(client, url, links, *, model) -> RelevantLinks`
  — LLM call #1; returns `response.parsed_output` (empty on refusal).
- `async build_brochure(client, name, pages, *, model) -> AsyncIterator[str]`
  — LLM call #2; async generator yielding brochure chunks.
- `async make_brochure(client, url, *, model, fetch_html=fetch_html) -> str`
  — orchestrates the pipeline, prints as it streams, returns the markdown.

> Unlike the other projects, the solution module is included as a worked
> example. The `__main__` block builds a real `AsyncAnthropic()` and fetches
> over the network; the graded functions never construct a client themselves.

## Run the tests

```bash
uv run pytest projects/brochure_generator/ -v
```

The suite mocks `client.messages.parse` (`AsyncMock`), fakes
`client.messages.stream` (an async context manager), and injects a fake
`fetch_html` — no API key, no network.

## Run it for real

Requires `ANTHROPIC_API_KEY` (in your environment or `.env`):

```bash
uv run python projects/brochure_generator/brochure.py https://www.anthropic.com
```

## Stretch goals

- Fetch the selected pages with a single shared `httpx.AsyncClient` instead of
  one per request.
- Add a `--tone` flag (e.g. serious vs. snarky) that swaps the brochure system
  prompt.
- Cap the number of selected pages, or the characters of text per page, before
  the brochure call.