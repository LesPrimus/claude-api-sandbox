# Brochure Generator — Design

**Date:** 2026-07-06
**Location:** `projects/brochure_generator/`
**Form:** Graded project (README brief + fully-mocked pytest suite + solution module)

## Goal

Given a company URL, produce a short marketing brochure in markdown by:

1. Scraping the landing page and collecting all links.
2. Making an LLM call (Claude) that selects only the **relevant** links, returned
   in a **structured** format.
3. Fetching each relevant page, then making a second LLM call that **streams** the
   brochure to stdout.

This composes three techniques already exercised elsewhere in the repo: async
`httpx` + BeautifulSoup scraping (`topics/streaming/01_low_level.py`), structured
outputs via `messages.parse()` (`projects/extractor/`), and streaming via
`messages.stream()` (`topics/streaming/02_stream_helper.py`). It is **async**
throughout, using `AsyncAnthropic` and `asyncio.gather` (`topics/async_usage/`).

## Architecture & data flow

```
url ──▶ fetch_html(url) ──▶ extract_links(html, url) ──▶ [urls]
                                                            │
                          select_relevant_links(client) ◀──┘   (LLM call #1, structured)
                                     │
                          RelevantLinks{links:[{type,url}]}
                                     │
              asyncio.gather(fetch_html) over selected urls (concurrent, fault-tolerant)
                                     │
              extract_text(html) per page → combined context
                                     │
                   build_brochure(client) ──▶ stream markdown  (LLM call #2, streaming)
```

Two LLM calls:

- **#1 — link selection:** structured output, returns `RelevantLinks`.
- **#2 — brochure:** streamed markdown.

Fetches for the selected links run concurrently via `asyncio.gather`. Scraping is
one level deep (landing page + each selected page); no recursion.

## Module contract — `projects/brochure_generator/brochure.py`

### Structured models (the "relevant links in a structured format")

```python
class Link(BaseModel):
    type: str   # e.g. "about page", "careers page", "products"
    url: str

class RelevantLinks(BaseModel):
    links: list[Link]
```

### Functions

All graded functions take an **injected `client`** so tests use a mock. Network
access lives behind an **injectable `fetch_html`** so tests stay fully offline.

- `async def fetch_html(url: str, *, http_client=None) -> str`
  Thin `httpx.AsyncClient` GET (follow redirects, a `User-Agent` header,
  `raise_for_status`). Returns raw HTML. `http_client` lets a caller/test pass an
  existing client; default constructs one.

- `def extract_links(html: str, base_url: str) -> list[str]`
  **Pure.** BeautifulSoup over `<a href>`; resolve relative → absolute with
  `urljoin`; keep only `http`/`https`; drop `mailto:`, `tel:`, bare `#` anchors;
  dedup preserving first-seen order.

- `def extract_text(html: str) -> str`
  **Pure.** Strip `script`/`style`/`noscript`, `get_text(separator="\n",
  strip=True)`.

- `async def select_relevant_links(client, url: str, links: list[str], *, model) -> RelevantLinks`  *(LLM #1)*
  `await client.messages.parse(model=..., max_tokens=..., messages=[...],
  output_format=RelevantLinks)`. Returns `response.parsed_output`; if it is
  `None`/refusal, returns `RelevantLinks(links=[])`. A system prompt tells Claude
  to keep brochure-relevant pages (About, Company, Careers, Products) and drop
  Terms/Privacy/login/social links. The candidate `links` are passed in the
  message.

- `async def build_brochure(client, name: str, pages, *, model) -> AsyncIterator[str]`  *(LLM #2)*
  Async generator. `async with client.messages.stream(...) as stream: async for
  text in stream.text_stream: yield text`. `pages` is the combined page context
  (label + text). System prompt: create a short markdown brochure for prospective
  customers/investors/recruits.

- `async def make_brochure(client, url: str, *, model, fetch_html=fetch_html) -> str`
  Orchestrator: `fetch_html(url)` → `extract_links` → `select_relevant_links` →
  concurrently `fetch_html` the selected urls (`asyncio.gather(...,
  return_exceptions=True)`, skipping failures) → `extract_text` each → stream
  `build_brochure`, printing chunks as they arrive, and return the assembled
  markdown string. Called by `__main__`.

### `__main__`

```python
async def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.anthropic.com"
    async with AsyncAnthropic() as client:
        await make_brochure(client, url)

if __name__ == "__main__":
    asyncio.run(main())
```

Company name is derived from the URL netloc (optional override parameter).

## Error handling

- **Selected-page fetches:** `asyncio.gather(..., return_exceptions=True)`; pages
  that error are skipped and the brochure is still built from what succeeded.
- **Landing-page fetch failure:** propagates (nothing to build from).
- **`select_relevant_links` refusal / no `parsed_output`:** return
  `RelevantLinks(links=[])`.
- **`extract_links`** filters non-http schemes so we never try to fetch
  `mailto:`/`tel:`.

## Testing — `test_brochure.py` (fully mocked, offline)

`asyncio_mode = "auto"` is already configured, so `async def test_*` run directly.
No network, no API key.

- `extract_links`: pure — feed an HTML string; assert absolute URLs, relative
  resolution, dedup, and that `mailto:`/`tel:`/`#` are dropped.
- `extract_text`: pure — assert `script`/`style` content removed, visible text
  returned.
- `select_relevant_links`: `AsyncMock` on `client.messages.parse` returning an
  object whose `.parsed_output` is a `RelevantLinks`; assert the function returns
  it, passes `output_format=RelevantLinks`, and includes the candidate links in
  the message. Also assert the refusal path returns `RelevantLinks(links=[])`.
- `build_brochure`: a fake async context manager for `client.messages.stream`
  whose `text_stream` is an async iterator of chunks; assert the chunks are
  streamed/assembled.
- `make_brochure`: inject a fake async `fetch_html` returning canned HTML, mock
  `parse` and `stream`; assert selected pages were fetched and the brochure text
  was assembled.

## Deliverables

- `projects/brochure_generator/README.md` — brief, exercises, contract, run
  command, stretch goals (matching the other projects' README style).
- `projects/brochure_generator/brochure.py` — the solution module.
- `projects/brochure_generator/test_brochure.py` — the fully-mocked graded suite.

## Non-goals (YAGNI)

- No recursive crawling beyond one level.
- No persistence/caching of fetched pages.
- No CLI framework — a positional URL arg is enough.
- No sync variant.