from enum import StrEnum, auto


class ModelType(StrEnum):
    HAIKU = "claude-haiku-4-5"
    SONNET = "claude-sonnet-4-6"
    OPUS = "claude-opus-4-8"


class Role(StrEnum):
    USER = auto()
    ASSISTANT = auto()
    SYSTEM = auto()
