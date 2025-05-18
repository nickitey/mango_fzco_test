from abc import ABC, abstractmethod

from src.domain.entities import User


class UserRepository(ABC):
    """
    Класс-репозиторий для работы с пользователем.
    В задании не оговорено, какой функционал работы с пользователями должен быть
    доступен, поэтому реализуем две базовые операции: создание и поиск по id.
    """

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        pass
