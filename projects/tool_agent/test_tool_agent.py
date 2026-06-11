"""Graded tests for Project 3 — Tool-Use Agent.

Fully mocked: no API key, no network. Implement `agent.py` to make these pass.
"""

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest


def _load():
    path = Path(__file__).parent / "agent.py"
    if not path.exists():
        pytest.fail(f"Not implemented yet — create {path.name} (see README.md)")
    spec = importlib.util.spec_from_file_location("agent", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def test_execute_tool_multiplies():
    agent = _load()
    assert agent.execute_tool("multiply", {"a": 6, "b": 7}) == "42"


def test_run_completes_the_tool_loop():
    agent = _load()
    client = MagicMock()
    client.messages.create.side_effect = [
        _tool_use_message("multiply", {"a": 6, "b": 7}, "toolu_1"),
        _text_message("6 times 7 is 42."),
    ]

    result = agent.run(client, "What is 6 times 7?")

    assert "42" in result
    assert client.messages.create.call_count == 2


def test_run_feeds_tool_result_back_with_matching_id():
    agent = _load()
    client = MagicMock()
    client.messages.create.side_effect = [
        _tool_use_message("multiply", {"a": 6, "b": 7}, "toolu_1"),
        _text_message("done"),
    ]

    agent.run(client, "multiply please")

    second_messages = client.messages.create.call_args_list[1].kwargs["messages"]
    tool_results = [
        block
        for msg in second_messages
        if isinstance(msg.get("content"), list)
        for block in msg["content"]
        if isinstance(block, dict) and block.get("type") == "tool_result"
    ]
    assert len(tool_results) == 1
    assert tool_results[0]["tool_use_id"] == "toolu_1"
    assert "42" in str(tool_results[0]["content"])


def test_run_passes_tools_to_the_api():
    agent = _load()
    client = MagicMock()
    client.messages.create.side_effect = [_text_message("no tools needed")]

    agent.run(client, "hi")

    assert client.messages.create.call_args.kwargs["tools"] == agent.TOOLS