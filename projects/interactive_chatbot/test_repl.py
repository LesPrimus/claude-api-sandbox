"""Graded tests for Project 7, Exercise 1 — REPL loop.

Fully mocked: no API key, no network. Implement `repl.py` to make these pass.
"""

from unittest.mock import MagicMock

SOLUTION = "repl.py"


def _conversation(*replies):
    """A stand-in Conversation whose send() returns the given replies in order."""
    conv = MagicMock()
    conv.send.side_effect = list(replies)
    return conv


def _scripted_input(*lines):
    """An input() replacement that yields each line, then raises EOFError."""
    return MagicMock(side_effect=[*lines, EOFError()])


def test_each_line_is_sent_and_reply_printed(solution):
    conv = _conversation("hi back", "bye then")
    out = []

    turns = solution.run_repl(
        conv,
        input_fn=_scripted_input("hello", "goodbye"),
        output_fn=out.append,
    )

    assert turns == 2
    assert [c.args[0] for c in conv.send.call_args_list] == ["hello", "goodbye"]
    assert out == ["hi back", "bye then"]


def test_exit_command_stops_without_sending(solution):
    conv = _conversation("should not be used")

    turns = solution.run_repl(
        conv,
        input_fn=_scripted_input("one", "exit", "two"),
        output_fn=MagicMock(),
    )

    assert turns == 1
    assert [c.args[0] for c in conv.send.call_args_list] == ["one"]


def test_quit_is_case_insensitive_and_stripped(solution):
    conv = _conversation()

    turns = solution.run_repl(
        conv,
        input_fn=_scripted_input("  QUIT  "),
        output_fn=MagicMock(),
    )

    assert turns == 0
    assert conv.send.call_count == 0


def test_blank_lines_are_skipped(solution):
    conv = _conversation("real reply")

    turns = solution.run_repl(
        conv,
        input_fn=_scripted_input("", "   ", "real question"),
        output_fn=MagicMock(),
    )

    assert turns == 1
    assert [c.args[0] for c in conv.send.call_args_list] == ["real question"]


def test_eof_ends_the_loop_cleanly(solution):
    conv = _conversation()

    # _scripted_input already raises EOFError after its lines; no input here.
    turns = solution.run_repl(
        conv,
        input_fn=MagicMock(side_effect=EOFError()),
        output_fn=MagicMock(),
    )

    assert turns == 0


def test_keyboard_interrupt_ends_the_loop_cleanly(solution):
    conv = _conversation()

    turns = solution.run_repl(
        conv,
        input_fn=MagicMock(side_effect=KeyboardInterrupt()),
        output_fn=MagicMock(),
    )

    assert turns == 0
