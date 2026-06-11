"""Graded tests for Project 1 — CLI Chatbot.

Fully mocked: no API key, no network. Implement `chatbot.py` to make these pass.
"""

from unittest.mock import MagicMock

SOLUTION = "chatbot.py"


def _text_message(text):
    block = MagicMock()
    block.type = "text"
    block.text = text
    msg = MagicMock()
    msg.content = [block]
    msg.usage.input_tokens = 10
    msg.usage.output_tokens = 5
    return msg


def _client_returning(*texts):
    client = MagicMock()
    client.messages.create.side_effect = [_text_message(t) for t in texts]
    return client


def test_send_returns_assistant_text(solution):
    client = _client_returning("Hi there!")
    conv = solution.Conversation(client)

    assert conv.send("hello") == "Hi there!"


def test_history_records_both_turns(solution):
    client = _client_returning("Hi there!")
    conv = solution.Conversation(client)
    conv.send("hello")

    assert conv.history == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]


def test_context_is_resent_on_second_turn(solution):
    client = _client_returning("First reply", "Second reply")
    conv = solution.Conversation(client)

    conv.send("one")
    conv.send("two")

    assert client.messages.create.call_count == 2
    second_messages = client.messages.create.call_args_list[1].kwargs["messages"]
    # On the 2nd call, the model must see turn 1 (user+assistant) then the new user msg.
    assert second_messages[:3] == [
        {"role": "user", "content": "one"},
        {"role": "assistant", "content": "First reply"},
        {"role": "user", "content": "two"},
    ]


def test_system_prompt_is_forwarded(solution):
    client = _client_returning("ok")
    conv = solution.Conversation(client, system="You are a terse assistant.")
    conv.send("hello")

    assert client.messages.create.call_args.kwargs["system"] == "You are a terse assistant."


def test_model_is_forwarded(solution):
    client = _client_returning("ok")
    conv = solution.Conversation(client, model="claude-haiku-4-5")
    conv.send("hello")

    assert client.messages.create.call_args.kwargs["model"] == "claude-haiku-4-5"