from abc import ABC, abstractmethod

from src.domain.entities import Chat


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
