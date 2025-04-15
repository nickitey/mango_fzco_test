from dataclasses import dataclass
from enum import Enum


class ChatCategory(Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


@dataclass
class Chat:
    id: int
    name: str
    category: ChatCategory
