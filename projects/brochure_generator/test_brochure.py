"""Graded tests for the Brochure Generator project.

Fully mocked: no API key, no network. Implement `brochure.py` to make these pass.

The Claude client and the page fetcher are both injected, so every test runs
offline:
- `client.messages.parse` is an ``AsyncMock`` (LLM call #1, structured links).
- `client.messages.stream` returns a fake async context manager (LLM call #2).
- `fetcher` is an ``AsyncMock`` returning canned HTML (no real HTTP).
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

SOLUTION = "brochure.py"


# --- fakes for the streaming helper -----------------------------------------


async def _achunks(chunks):
    """An async iterator over ``chunks`` — stands in for ``stream.text_stream``."""
    for chunk in chunks:
        yield chunk


class _FakeStreamCM:
    """Async context manager mimicking ``client.messages.stream(...)``."""

    def __init__(self, chunks):
        self.text_stream = _achunks(chunks)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


# --- extract_links (pure) ----------------------------------------------------


def test_extract_links_resolves_relative_and_dedups(solution):
    html = """
      <a href="/about">About</a>
      <a href="about">About (relative)</a>
      <a href="https://other.com/x">External</a>
      <a href="/about">About again</a>
    """
    links = solution.extract_links(html, "https://acme.com/")

    assert "https://acme.com/about" in links
    assert "https://other.com/x" in links
    assert links.count("https://acme.com/about") == 1  # deduped


def test_extract_links_drops_non_http_schemes(solution):
    html = """
      <a href="mailto:a@b.com">Mail</a>
      <a href="tel:+123">Call</a>
      <a href="#top">Top anchor</a>
      <a href="/real">Real</a>
    """
    links = solution.extract_links(html, "https://acme.com/")

    assert links == ["https://acme.com/real"]


# --- extract_text (pure) -----------------------------------------------------


def test_extract_text_strips_scripts_and_returns_visible_text(solution):
    html = (
        "<html><head><style>b{color:red}</style></head>"
        "<body><script>var x = 1;</script><h1>Hello</h1><p>World</p></body></html>"
    )
    text = solution.extract_text(html)

    assert "Hello" in text
    assert "World" in text
    assert "var x" not in text
    assert "color:red" not in text


# --- select_relevant_links (LLM call #1) -------------------------------------


def _client_parsing(parsed_output):
    client = MagicMock()
    client.messages.parse = AsyncMock(
        return_value=SimpleNamespace(parsed_output=parsed_output)
    )
    return client


async def test_select_relevant_links_returns_parsed_output(solution):
    relevant = solution.RelevantLinks(
        links=[solution.Link(type="about page", url="https://x.com/about")]
    )
    client = _client_parsing(relevant)

    result = await solution.select_relevant_links(
        client, "https://x.com", ["https://x.com/about", "https://x.com/tos"]
    )

    assert result is relevant


async def test_select_relevant_links_passes_output_format_and_links(solution):
    client = _client_parsing(solution.RelevantLinks(links=[]))

    await solution.select_relevant_links(
        client, "https://x.com", ["https://x.com/about"]
    )

    kwargs = client.messages.parse.call_args.kwargs
    assert kwargs["output_format"] is solution.RelevantLinks
    assert "https://x.com/about" in str(kwargs["messages"])


async def test_select_relevant_links_empty_on_refusal(solution):
    client = _client_parsing(None)  # refusal / no parsed_output

    result = await solution.select_relevant_links(client, "https://x.com", [])

    assert isinstance(result, solution.RelevantLinks)
    assert result.links == []


# --- build_brochure (LLM call #2, streaming) ---------------------------------


async def test_build_brochure_streams_chunks(solution):
    client = MagicMock()
    client.messages.stream.return_value = _FakeStreamCM(["Hello ", "world", "!"])
    pages = [("landing page", "Acme makes widgets.")]

    out = [
        chunk
        async for chunk in solution.build_brochure(
            client, "acme.com", pages, model="test-model"
        )
    ]

    assert "".join(out) == "Hello world!"
    assert client.messages.stream.called


# --- make_brochure (orchestration) -------------------------------------------


async def test_make_brochure_fetches_selected_pages_and_assembles(solution):
    landing = (
        '<html><body><a href="/about">About</a>'
        '<a href="/careers">Careers</a></body></html>'
    )
    pages_by_url = {
        "https://acme.com": landing,
        "https://acme.com/about": "<h1>About Acme</h1><p>We build things.</p>",
        "https://acme.com/careers": "<h1>Join us</h1>",
    }
    fetcher = AsyncMock(side_effect=lambda url, **kw: pages_by_url[url])

    client = MagicMock()
    relevant = solution.RelevantLinks(
        links=[
            solution.Link(type="about page", url="https://acme.com/about"),
            solution.Link(type="careers page", url="https://acme.com/careers"),
        ]
    )
    client.messages.parse = AsyncMock(
        return_value=SimpleNamespace(parsed_output=relevant)
    )
    client.messages.stream.return_value = _FakeStreamCM(["Brochure ", "text"])

    result = await solution.make_brochure(client, "https://acme.com", fetcher=fetcher)

    assert result == "Brochure text"
    fetched = {call.args[0] for call in fetcher.await_args_list}
    assert "https://acme.com/about" in fetched
    assert "https://acme.com/careers" in fetched


async def test_make_brochure_skips_pages_that_fail_to_fetch(solution):
    landing = '<html><body><a href="/about">About</a></body></html>'

    async def fetcher(url, **kw):
        if url == "https://acme.com":
            return landing
        raise RuntimeError("boom")  # every selected page fails

    client = MagicMock()
    relevant = solution.RelevantLinks(
        links=[solution.Link(type="about page", url="https://acme.com/about")]
    )
    client.messages.parse = AsyncMock(
        return_value=SimpleNamespace(parsed_output=relevant)
    )
    client.messages.stream.return_value = _FakeStreamCM(["ok"])

    # A failed page fetch must not blow up the whole brochure.
    result = await solution.make_brochure(client, "https://acme.com", fetcher=fetcher)

    assert result == "ok"
