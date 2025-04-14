from abc import ABC, abstractmethod

from src.domain.entities import Group


class GroupRepository(ABC):
    """
    Класс-репозиторий для работы с группой.
    В задании не оговорено, какой функционал работы с группами должен быть
    доступен, поэтому реализуем две базовые операции: создание и поиск по id.

    """
    @abstractmethod
    async def get_by_chat_id(self, chat_id: int) -> Group | None:
        pass

    @abstractmethod
    async def get_by_group_id(self, group_id: int) -> Group | None:
        pass

    @abstractmethod
    async def create(self, group: Group) -> Group:
        pass
