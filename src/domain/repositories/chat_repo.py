from abc import ABC, abstractmethod
from typing import NoReturn

from src.domain.entities import Chat, User


class ChatRepository(ABC):
    """
    Класс-репозиторий для работы с чатом.
    В задании не оговорено, какой функционал работы с чатами должен быть
    доступен, поэтому реализуем две базовые операции: создание и поиск по id.
    """

    @abstractmethod
    async def get_by_id(self, chat_id: int) -> Chat | None:
        pass

    @abstractmethod
    async def create(self, chat: Chat) -> Chat:
        pass

    @abstractmethod
    async def validate_users(
        self, participant_ids: list[int]
    ) -> None | NoReturn:
        pass

    @abstractmethod
    async def get_chat_participants(self, chat_id: int) -> list[User | None]:
        pass

    @abstractmethod
    async def check_chat_participant(self, chat_id: int, user_id: int) -> bool:
        pass
