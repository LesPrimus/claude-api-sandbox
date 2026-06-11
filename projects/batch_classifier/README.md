# Project 5 — Batch Classifier

Classify a whole list of items in one shot using the **Batches API** — async
processing at 50% of standard cost. You submit many requests, poll until the
batch finishes, then collect the results by `custom_id`.

## Exercises

- Building `Request` / `MessageCreateParamsNonStreaming` objects
- `client.messages.batches.create` / `.retrieve` / `.results`
- Polling on `processing_status` and mapping results back by `custom_id`

## What to build

Create `projects/batch_classifier/classifier.py` with three functions:

```python
def build_requests(items: list[str], *, model: str = "claude-haiku-4-5") -> list:
    """One batch Request per item, custom_id = f'item-{i}'."""

def parse_results(results) -> dict[str, str]:
    """Map custom_id -> the text label for each succeeded result."""

def classify(client, items: list[str], *, poll_interval: float = 5.0) -> dict[str, str]:
    """Create the batch, poll until ended, return {custom_id: label}."""
```

### Contract

`build_requests`:
- Use `Request(custom_id=..., params=MessageCreateParamsNonStreaming(...))` from
  `anthropic.types.messages.batch_create_params` / `anthropic.types.message_create_params`.
- `custom_id` for item `i` must be `f"item-{i}"`.
- The prompt should ask Claude to classify the item; include the item text.

`parse_results`:
- Iterate `results`. For each whose `result.type == "succeeded"`, read the first
  `text` block of `result.message.content` and map `custom_id -> text.strip()`.

`classify`:
- `batch = client.messages.batches.create(requests=build_requests(items))`.
- Poll: `client.messages.batches.retrieve(batch.id)` until
  `processing_status == "ended"` (sleep `poll_interval` between polls).
- Return `parse_results(client.messages.batches.results(batch.id))`.

> The tests make `retrieve` report `"ended"` immediately (so no real sleeping),
> mock `results` with two succeeded items, and assert the returned mapping.

## Run the tests

```bash
uv run pytest projects/batch_classifier/ -v
```

## Stretch goals

- Handle `errored` / `expired` results instead of skipping them.
- Add prompt caching of a shared system prompt across all requests.
- Write results out to a CSV keyed by the original item.