"""Graded tests for Project 7, Exercise 2 — Streaming replies.

Fully mocked: no API key, no network. Implement `streaming.py` to make these pass.
"""

from unittest.mock import MagicMock

SOLUTION = "streaming.py"


def _streaming_client(*chunks):
    """A client whose messages.stream() context manager yields the given chunks."""
    stream = MagicMock()
    stream.text_stream = iter(chunks)

    cm = MagicMock()
    cm.__enter__.return_value = stream
    cm.__exit__.return_value = False

    client = MagicMock()
    client.messages.stream.return_value = cm
    return client


def test_send_returns_joined_chunks(solution):
    client = _streaming_client("Hel", "lo ", "world")
    conv = solution.StreamingConversation(client)

    assert conv.send("hi") == "Hello world"


def test_on_text_called_per_chunk(solution):
    client = _streaming_client("a", "b", "c")
    conv = solution.StreamingConversation(client)
    seen = []

    conv.send("hi", on_text=seen.append)

    assert seen == ["a", "b", "c"]


def test_history_records_both_turns(solution):
    client = _streaming_client("Hi ", "there")
    conv = solution.StreamingConversation(client)

    conv.send("hello")

    assert conv.history == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "Hi there"},
    ]


def test_context_is_resent_on_second_turn(solution):
    client = _streaming_client("first")
    conv = solution.StreamingConversation(client)
    conv.send("one")

    # second turn uses a fresh stream
    client.messages.stream.return_value.__enter__.return_value.text_stream = iter(
        ["second"]
    )
    conv.send("two")

    second_messages = client.messages.stream.call_args_list[1].kwargs["messages"]
    assert second_messages[:3] == [
        {"role": "user", "content": "one"},
        {"role": "assistant", "content": "first"},
        {"role": "user", "content": "two"},
    ]


def test_model_is_forwarded_to_stream(solution):
    client = _streaming_client("ok")
    conv = solution.StreamingConversation(client, model="claude-haiku-4-5")
    conv.send("hello")

    assert client.messages.stream.call_args.kwargs["model"] == "claude-haiku-4-5"


def test_system_prompt_is_forwarded_when_set(solution):
    client = _streaming_client("ok")
    conv = solution.StreamingConversation(client, system="You are terse.")
    conv.send("hello")

    assert client.messages.stream.call_args.kwargs["system"] == "You are terse."
