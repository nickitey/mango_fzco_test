from dataclasses import dataclass, field
from typing import Any


@dataclass
class Group:
    name: str
    creator: int
    participants: list[Any]
    chat_id: int
    id: int | None = field(default=None)
    # Начиная с python3.9 можно использовать класс list для аннотации.
    # Источник: https://peps.python.org/pep-0585/
    # Отход от использования для аннотации typing.List НЕ является ошибкой.
    # Некоторые староверы настаивают на использовании typing.List, поэтому
    # я оговариваю это особо.
