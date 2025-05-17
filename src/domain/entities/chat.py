from dataclasses import dataclass, field
from enum import Enum


class ChatCategory(Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


@dataclass
class Chat:
    name: str
    category: ChatCategory
    participants: list[int]
    id: int | None = field(default=None)
