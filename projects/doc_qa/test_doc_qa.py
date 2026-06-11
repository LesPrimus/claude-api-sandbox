"""Graded tests for Project 2 — Document Q&A.

Fully mocked: no API key, no network. Implement `doc_qa.py` to make these pass.
"""

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest


def _load():
    path = Path(__file__).parent / "doc_qa.py"
    if not path.exists():
        pytest.fail(f"Not implemented yet — create {path.name} (see README.md)")
    spec = importlib.util.spec_from_file_location("doc_qa", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _text_message(text):
    block = MagicMock()
    block.type = "text"
    block.text = text
    msg = MagicMock()
    msg.content = [block]
    return msg


def _client():
    client = MagicMock()
    client.beta.files.upload.return_value.id = "file_abc123"
    client.beta.messages.create.return_value = _text_message("The answer is 42.")
    return client


def test_upload_returns_file_id():
    doc_qa = _load()
    client = _client()

    assert doc_qa.upload_document(client, "report.pdf") == "file_abc123"
    assert client.beta.files.upload.called


def test_ask_returns_answer_text():
    doc_qa = _load()
    client = _client()

    assert doc_qa.ask(client, "file_abc123", "What is the answer?") == "The answer is 42."


def test_ask_references_the_file_id_in_a_document_block():
    doc_qa = _load()
    client = _client()
    doc_qa.ask(client, "file_abc123", "What is the answer?")

    kwargs = client.beta.messages.create.call_args.kwargs
    messages_repr = str(kwargs["messages"])
    assert "document" in messages_repr
    assert "file_abc123" in messages_repr
    assert "What is the answer?" in messages_repr


def test_ask_sets_files_beta_header():
    doc_qa = _load()
    client = _client()
    doc_qa.ask(client, "file_abc123", "anything")

    assert "files-api-2025-04-14" in client.beta.messages.create.call_args.kwargs["betas"]