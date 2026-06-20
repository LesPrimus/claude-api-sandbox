"""Graded tests for Project 4 — Structured Extractor.

Fully mocked: no API key, no network. Implement `extractor.py` to make these pass.
"""

from unittest.mock import MagicMock

SOLUTION = "extractor.py"

SAMPLE = "Jane Doe (jane@co.com) is interested in the API and the SDKs."


def _client_returning(contact):
    client = MagicMock()
    client.messages.parse.return_value.parsed_output = contact
    return client


def test_contact_model_shape(solution):
    c = solution.Contact(
        name="Jane Doe", email="jane@co.com", interests=["API", "SDKs"]
    )
    assert c.name == "Jane Doe"
    assert c.email == "jane@co.com"
    assert c.interests == ["API", "SDKs"]


def test_extract_returns_parsed_contact(solution):
    expected = solution.Contact(
        name="Jane Doe", email="jane@co.com", interests=["API", "SDKs"]
    )
    client = _client_returning(expected)

    result = solution.extract(client, SAMPLE)

    assert isinstance(result, solution.Contact)
    assert result == expected


def test_extract_uses_parse_with_the_model_as_output_format(solution):
    expected = solution.Contact(name="X", email="x@y.com", interests=[])
    client = _client_returning(expected)

    solution.extract(client, SAMPLE)

    assert client.messages.parse.called
    assert (
        client.messages.parse.call_args.kwargs.get("output_format") is solution.Contact
    )


def test_extract_sends_the_text_to_the_model(solution):
    expected = solution.Contact(name="X", email="x@y.com", interests=[])
    client = _client_returning(expected)

    solution.extract(client, SAMPLE)

    assert SAMPLE in str(client.messages.parse.call_args.kwargs["messages"])
