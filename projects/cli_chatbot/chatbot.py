from typing import Literal, cast

from anthropic import Client, omit, Omit
from anthropic.types import MessageParam, Message, TextBlock
from dotenv import load_dotenv

from projects._models import ModelType


load_dotenv()


class Conversation:
    def __init__(
        self,
        client: Client,
        *,
        model: str = ModelType.HAIKU,
        system: str | Omit = omit,
        max_tokens: int = 1024,
    ) -> None:

        self._client = client
        self._model = model
        self._system = system
        self._max_tokens = max_tokens
        self._history: list[MessageParam] = []

    @property
    def history(self) -> list[MessageParam]:
        return self._history

    @staticmethod
    def _create_message_param(
        role: Literal["user", "assistant", "system"], content: str
    ) -> MessageParam:
        return MessageParam(
            role=role,
            content=content,
        )

    def _send(self) -> Message:
        return self._client.messages.create(
            max_tokens=self._max_tokens,
            messages=self._history,
            model=self._model,
            system=self._system,
        )

    def send(self, user_message: str) -> str:
        self._history.append(self._create_message_param("user", user_message))
        message: Message = self._send()
        text = next(
            (cast(TextBlock, b).text for b in message.content if b.type == "text"), ""
        )
        self._history.append(self._create_message_param("assistant", text))
        return text


if __name__ == "__main__":
    chat = Conversation(client=Client())
    print(chat.send("Hi Claude!!"))
    print(chat.send("Just trying the api"))
