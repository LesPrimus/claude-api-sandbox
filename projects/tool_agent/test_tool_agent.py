"""Graded tests for Project 3 — Tool-Use Agent.

Fully mocked: no API key, no network. Implement `agent.py` to make these pass.
"""

from unittest.mock import MagicMock

SOLUTION = "agent.py"


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


def test_execute_tool_multiplies(solution):
    assert solution.execute_tool("multiply", {"a": 6, "b": 7}) == "42"


def test_run_completes_the_tool_loop(solution):
    client = MagicMock()
    client.messages.create.side_effect = [
        _tool_use_message("multiply", {"a": 6, "b": 7}, "toolu_1"),
        _text_message("6 times 7 is 42."),
    ]

    result = solution.run(client, "What is 6 times 7?")

    assert "42" in result
    assert client.messages.create.call_count == 2


def test_run_feeds_tool_result_back_with_matching_id(solution):
    client = MagicMock()
    client.messages.create.side_effect = [
        _tool_use_message("multiply", {"a": 6, "b": 7}, "toolu_1"),
        _text_message("done"),
    ]

    solution.run(client, "multiply please")

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


def test_run_passes_tools_to_the_api(solution):
    client = MagicMock()
    client.messages.create.side_effect = [_text_message("no tools needed")]

    solution.run(client, "hi")

    assert client.messages.create.call_args.kwargs["tools"] == solution.TOOLS
