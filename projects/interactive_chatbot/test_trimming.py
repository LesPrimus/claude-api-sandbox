"""Graded tests for Project 7, Exercise 3 — Trim to a token budget.

Fully mocked: no API key, no network. Implement `trimming.py` to make these pass.
"""

from unittest.mock import MagicMock

SOLUTION = "trimming.py"


def _counting_client(*counts):
    """A client whose count_tokens() returns each given .input_tokens in order."""
    client = MagicMock()
    client.messages.count_tokens.side_effect = [
        MagicMock(input_tokens=c) for c in counts
    ]
    return client


def _turns(n):
    """n user+assistant turns -> 2n messages."""
    msgs = []
    for i in range(n):
        msgs.append({"role": "user", "content": f"q{i}"})
        msgs.append({"role": "assistant", "content": f"a{i}"})
    return msgs


def test_under_budget_returns_unchanged(solution):
    client = _counting_client(50)
    history = _turns(3)

    result = solution.trim_to_budget(client, history, model="m", budget=100)

    assert result == history
    assert client.messages.count_tokens.call_count == 1


def test_drops_oldest_turns_until_within_budget(solution):
    client = _counting_client(300, 200, 100)  # over, over, then ok
    history = _turns(3)  # 6 messages

    result = solution.trim_to_budget(client, history, model="m", budget=150)

    # dropped the two oldest turns, kept the most recent one
    assert result == history[-2:]
    assert client.messages.count_tokens.call_count == 3


def test_keeps_at_least_the_last_turn(solution):
    client = _counting_client(999, 999, 999, 999)  # always over budget
    history = _turns(3)

    result = solution.trim_to_budget(client, history, model="m", budget=10)

    # never empties the transcript: the last turn survives
    assert result == history[-2:]


def test_does_not_mutate_caller_list(solution):
    client = _counting_client(300, 100)
    history = _turns(2)
    snapshot = list(history)

    solution.trim_to_budget(client, history, model="m", budget=150)

    assert history == snapshot


def test_model_and_system_forwarded_to_count_tokens(solution):
    client = _counting_client(50)
    history = _turns(1)

    solution.trim_to_budget(
        client, history, model="claude-haiku-4-5", budget=100, system="hi"
    )

    kwargs = client.messages.count_tokens.call_args.kwargs
    assert kwargs["model"] == "claude-haiku-4-5"
    assert kwargs["system"] == "hi"
