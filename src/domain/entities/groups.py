from dataclasses import dataclass


@dataclass
class Group:
    id: int
    name: str
    creator_id: int
    participants: list[int]
    # Начиная с python3.9 можно использовать класс list для аннотации.
    # Источник: https://peps.python.org/pep-0585/
    # Отход от использования для аннотации typing.List НЕ является ошибкой.
    # Некоторые староверы настаивают на использовании typing.List, поэтому
    # я оговариваю это особо.
