"""Brochure Generator.

Given a company URL, produce a short marketing brochure in markdown:

1. Scrape the landing page and collect all links.
2. Ask Claude to select only the brochure-relevant links, returned in a
   structured format (LLM call #1, ``messages.parse``).
3. Fetch each selected page, then stream the brochure (LLM call #2,
   ``messages.stream``).

Everything is async: ``AsyncAnthropic`` for Claude, ``httpx.AsyncClient`` for
fetching, and ``asyncio.gather`` to fetch the selected pages concurrently.

The graded functions take an injected ``client`` and an injectable
``fetch_html`` so the test suite runs fully offline. The ``__main__`` block
builds a real ``AsyncAnthropic`` and fetches over the network.
"""

import asyncio
import sys
from collections.abc import AsyncIterator
from urllib.parse import urldefrag, urljoin, urlparse

import httpx
from anthropic import AsyncAnthropic
from anthropic.types import MessageParam
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pydantic import BaseModel

from projects._models import ModelType

load_dotenv()

USER_AGENT = "Mozilla/5.0 (compatible; claude-brochure/1.0)"

SELECT_SYSTEM = """
You are given a list of links found on a company's landing page. Decide which
links are relevant to include in a short brochure about the company for
prospective customers, investors, and job applicants — for example an About /
Company page, a Careers / Jobs page, and a Products or Pricing page.

Exclude links that are not useful for a brochure: Terms of Service, Privacy
Policy, login pages, email addresses, and social-media links. Respond with
absolute URLs exactly as they appear in the list.
""".strip()

BROCHURE_SYSTEM = """
You are an assistant that creates a short, engaging brochure about a company
for prospective customers, investors, and recruits. You are given the text of
several pages from the company's website.

Write the brochure in clean markdown. Respond with only the brochure — no
preamble, and do not wrap it in a code block.
""".strip()


class Link(BaseModel):
    """A single relevant link, categorised by the kind of page it points to."""

    type: str  # e.g. "about page", "careers page", "products"
    url: str


class RelevantLinks(BaseModel):
    """The structured result of the link-selection step."""

    links: list[Link]


async def fetch_html(url: str) -> str:
    """Fetch a URL and return its raw HTML.

    Creates a short-lived ``httpx`` client for the request and closes it on exit.
    """
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        return response.text


def extract_links(html: str, base_url: str) -> list[str]:
    """Extract absolute http(s) links from ``html``.

    Relative hrefs are resolved against ``base_url``; ``mailto:``/``tel:`` and
    bare ``#`` anchors are dropped; fragments are stripped and duplicates
    removed while preserving first-seen order.
    """
    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    links: list[str] = []

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue

        absolute, _ = urldefrag(urljoin(base_url, href))
        if urlparse(absolute).scheme not in ("http", "https"):
            continue

        if absolute not in seen:
            seen.add(absolute)
            links.append(absolute)

    return links


def extract_text(html: str) -> str:
    """Return the visible text of ``html``, stripped of scripts and styles."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


async def select_relevant_links(
    client: AsyncAnthropic,
    url: str,
    links: list[str],
    *,
    model: str = ModelType.OPUS,
) -> RelevantLinks:
    """Ask Claude which links belong in a brochure (structured output)."""
    joined = "\n".join(links)
    messages: list[MessageParam] = [
        {
            "role": "user",
            "content": (
                f"These are the links found on {url}. Select the ones relevant "
                f"for a company brochure:\n\n{joined}"
            ),
        }
    ]

    response = await client.messages.parse(
        model=model,
        max_tokens=1024,
        system=SELECT_SYSTEM,
        messages=messages,
        output_format=RelevantLinks,
    )

    # parsed_output is absent/None on a refusal — fall back to an empty result.
    return response.parsed_output or RelevantLinks(links=[])


async def build_brochure(
    client: AsyncAnthropic,
    company_name: str,
    pages: list[tuple[str, str]],
    *,
    model: str = ModelType.OPUS,
) -> AsyncIterator[str]:
    """Stream a markdown brochure from the collected page text.

    ``pages`` is a list of ``(label, text)`` pairs. Yields text chunks as they
    arrive so the caller can print them live.
    """
    body = "\n\n".join(f"## {label}\n{text}" for label, text in pages)
    messages: list[MessageParam] = [
        {
            "role": "user",
            "content": (
                f"Company: {company_name}\n\n"
                f"Here are the contents of its web pages. Use them to build the "
                f"brochure:\n\n{body}"
            ),
        }
    ]

    async with client.messages.stream(
        model=model,
        max_tokens=4096,
        system=BROCHURE_SYSTEM,
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            yield text


async def make_brochure(
    client: AsyncAnthropic,
    url: str,
    *,
    model: str = ModelType.OPUS,
    fetcher=fetch_html,
) -> str:
    """Scrape ``url``, select relevant links, and stream a brochure.

    Prints the brochure as it streams and returns the assembled markdown.
    Page fetches for the selected links run concurrently; a page that fails to
    fetch is skipped rather than aborting the whole brochure.
    """
    landing_html = await fetcher(url)
    links = extract_links(landing_html, url)
    relevant = await select_relevant_links(client, url, links, model=model)

    fetched = await asyncio.gather(
        *(fetcher(link.url) for link in relevant.links),
        return_exceptions=True,
    )

    pages: list[tuple[str, str]] = [("landing page", extract_text(landing_html))]
    for link, html in zip(relevant.links, fetched):
        if isinstance(html, BaseException):
            continue
        pages.append((link.type, extract_text(html)))

    company_name = urlparse(url).netloc or url
    collected: list[str] = []
    async for chunk in build_brochure(client, company_name, pages, model=model):
        print(chunk, end="", flush=True)
        collected.append(chunk)
    print()

    return "".join(collected)


async def _amain() -> None:
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.anthropic.com"
    async with AsyncAnthropic() as client:
        await make_brochure(client, url)


if __name__ == "__main__":
    asyncio.run(_amain())
