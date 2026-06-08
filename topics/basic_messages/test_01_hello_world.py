import importlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

mod = importlib.import_module("topics.basic_messages.01_hello_world")


@pytest.fixture
def mock_message():
    content = MagicMock()
    content.text = "Hello!"
    msg = MagicMock()
    msg.content = [content]
    msg.usage.input_tokens = 10
    msg.usage.output_tokens = 5
    return msg


async def test_main_returns_response(mock_message):
    with patch.object(
        mod.client.messages, "create", new=AsyncMock(return_value=mock_message)
    ):
        result = await mod.main()

    assert result.text == "Hello!"
    assert result.input_tokens == 10
    assert result.output_tokens == 5
