"""Graded tests for Project 6 — Coding Assistant.

Fully mocked: no API key, no network. Implement `assistant.py` to make these pass.
"""

from unittest.mock import MagicMock

import pytest

SOLUTION = "assistant.py"


def _tool_use_message(name, tool_input, tool_id):
    block = MagicMock()
    block.type = "tool_use"
    block.name = name
    block.input = tool_input
    block.id = tool_id
    msg = MagicMock()
    msg.content = [block]
    msg.stop_reason = "tool_use"
    return msg


def _text_message(text):
    block = MagicMock()
    block.type = "text"
    block.text = text
    msg = MagicMock()
    msg.content = [block]
    msg.stop_reason = "end_turn"
    return msg


def _write_then_done(path, content):
    return [
        _tool_use_message("write_file", {"path": path, "content": content}, "toolu_1"),
        _text_message("Done."),
    ]


def test_safe_path_allows_paths_inside_workdir(solution, tmp_path):
    resolved = solution.safe_path(tmp_path, "notes/todo.txt")
    assert str(resolved).startswith(str(tmp_path.resolve()))


def test_safe_path_rejects_traversal(solution, tmp_path):
    with pytest.raises(ValueError):
        solution.safe_path(tmp_path, "../escape.txt")


def test_write_happens_when_approved(solution, tmp_path):
    client = MagicMock()
    client.messages.create.side_effect = _write_then_done("hello.txt", "hi there")

    result = solution.run(
        client, "create hello.txt", workdir=tmp_path, approve=lambda n, i: True
    )

    assert (tmp_path / "hello.txt").read_text() == "hi there"
    assert "Done." in result


def test_write_is_blocked_when_denied(solution, tmp_path):
    client = MagicMock()
    client.messages.create.side_effect = _write_then_done("hello.txt", "hi there")

    result = solution.run(
        client, "create hello.txt", workdir=tmp_path, approve=lambda n, i: False
    )

    assert not (tmp_path / "hello.txt").exists()
    assert "Done." in result  # loop still completes after the denied write


def test_approve_is_called_with_tool_name_and_input(solution, tmp_path):
    client = MagicMock()
    client.messages.create.side_effect = _write_then_done("a.txt", "data")
    approve = MagicMock(return_value=True)

    solution.run(client, "write a.txt", workdir=tmp_path, approve=approve)

    approve.assert_called_once_with("write_file", {"path": "a.txt", "content": "data"})


def test_adaptive_thinking_is_enabled(solution, tmp_path):
    client = MagicMock()
    client.messages.create.side_effect = [_text_message("nothing to do")]

    solution.run(client, "hi", workdir=tmp_path)

    assert client.messages.create.call_args.kwargs["thinking"] == {"type": "adaptive"}
