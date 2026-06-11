"""Graded tests for Project 4 — Structured Extractor.

Fully mocked: no API key, no network. Implement `extractor.py` to make these pass.
"""

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest


def _load():
    path = Path(__file__).parent / "extractor.py"
    if not path.exists():
        pytest.fail(f"Not implemented yet — create {path.name} (see README.md)")
    spec = importlib.util.spec_from_file_location("extractor", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SAMPLE = "Jane Doe (jane@co.com) is interested in the API and the SDKs."


def _client_returning(contact):
    client = MagicMock()
    client.messages.parse.return_value.parsed_output = contact
    return client


def test_contact_model_shape():
    extractor = _load()
    c = extractor.Contact(name="Jane Doe", email="jane@co.com", interests=["API", "SDKs"])
    assert c.name == "Jane Doe"
    assert c.email == "jane@co.com"
    assert c.interests == ["API", "SDKs"]


def test_extract_returns_parsed_contact():
    extractor = _load()
    expected = extractor.Contact(name="Jane Doe", email="jane@co.com", interests=["API", "SDKs"])
    client = _client_returning(expected)

    result = extractor.extract(client, SAMPLE)

    assert isinstance(result, extractor.Contact)
    assert result == expected


def test_extract_uses_parse_with_the_model_as_output_format():
    extractor = _load()
    expected = extractor.Contact(name="X", email="x@y.com", interests=[])
    client = _client_returning(expected)

    extractor.extract(client, SAMPLE)

    assert client.messages.parse.called
    assert client.messages.parse.call_args.kwargs.get("output_format") is extractor.Contact


def test_extract_sends_the_text_to_the_model():
    extractor = _load()
    expected = extractor.Contact(name="X", email="x@y.com", interests=[])
    client = _client_returning(expected)

    extractor.extract(client, SAMPLE)

    assert SAMPLE in str(client.messages.parse.call_args.kwargs["messages"])