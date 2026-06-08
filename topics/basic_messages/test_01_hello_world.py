import importlib
from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock

mod = importlib.import_module("topics.basic_messages.01_hello_world")


@contextmanager
def patch_async_anthropic(mock_client):
    original = mod.AsyncAnthropic
    mod.AsyncAnthropic = lambda: mock_client
    try:
        yield
    finally:
        mod.AsyncAnthropic = original


async def test_main_returns_response():
    content = MagicMock()
    content.text = "Hello!"
    msg = MagicMock()
    msg.content = [content]
    msg.usage.input_tokens = 10
    msg.usage.output_tokens = 5

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=msg)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch_async_anthropic(mock_client):
        result = await mod.main()

    assert result.text == "Hello!"
    assert result.input_tokens == 10
    assert result.output_tokens == 5
