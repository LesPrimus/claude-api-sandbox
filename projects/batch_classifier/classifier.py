import time

from anthropic import Anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request


def build_requests(items: list[str], *, model: str = "claude-haiku-4-5") -> list:
    """One batch Request per item, custom_id = f'item-{i}'."""
    return [
        Request(
            custom_id=f"item-{i}",
            params=MessageCreateParamsNonStreaming(
                model=model,
                max_tokens=64,
                messages=[{"role": "user", "content": f"Classify this: {item}"}],  # noqa
            ),
        )
        for i, item in enumerate(items)
    ]

def parse_results(results) -> dict[str, str]:
    """Map custom_id -> the text label for each succeeded result."""
    return {
        result.custom_id: result.result.message.content[0].text.strip()
        for result in results
        if result.result.type == "succeeded"
    }


def classify(client: Anthropic, items: list[str], *, poll_interval: float = 5.0) -> dict[str, str]:
    """Create the batch, poll until ended, return {custom_id: label}."""
    message_batch = client.messages.batches.create(requests=build_requests(items))

    while True:
        batch = client.messages.batches.retrieve(message_batch.id)
        if batch.processing_status == "ended":
            results = client.messages.batches.results(message_batch.id)
            return parse_results(results)
        time.sleep(poll_interval)

