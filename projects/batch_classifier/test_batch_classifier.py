"""Graded tests for Project 5 — Batch Classifier.

Fully mocked: no API key, no network. Implement `classifier.py` to make these pass.
"""

from unittest.mock import MagicMock

SOLUTION = "classifier.py"


def _succeeded_result(custom_id, label):
    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = label
    result = MagicMock()
    result.custom_id = custom_id
    result.result.type = "succeeded"
    result.result.message.content = [text_block]
    return result


def test_build_requests_assigns_custom_ids(solution):
    reqs = solution.build_requests(["great product", "awful support"])

    assert len(reqs) == 2
    assert reqs[0]["custom_id"] == "item-0"
    assert reqs[1]["custom_id"] == "item-1"
    assert "great product" in str(reqs[0])


def test_parse_results_maps_custom_id_to_label(solution):
    results = [
        _succeeded_result("item-0", "positive"),
        _succeeded_result("item-1", "negative"),
    ]

    assert solution.parse_results(results) == {"item-0": "positive", "item-1": "negative"}


def test_classify_creates_polls_and_returns_mapping(solution):
    client = MagicMock()
    client.messages.batches.create.return_value.id = "batch_1"
    client.messages.batches.retrieve.return_value.processing_status = "ended"
    client.messages.batches.results.return_value = [
        _succeeded_result("item-0", "positive"),
        _succeeded_result("item-1", "negative"),
    ]

    out = solution.classify(client, ["great product", "awful support"], poll_interval=0)

    assert out == {"item-0": "positive", "item-1": "negative"}
    assert client.messages.batches.create.called
    assert client.messages.batches.results.call_args.args[0] == "batch_1"