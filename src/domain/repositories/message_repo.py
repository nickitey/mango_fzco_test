from abc import ABC, abstractmethod

from src.domain.entities import Message


class MessageRepository(ABC):
    """
    Класс-репозиторий для работы с сообщением.
    Помимо очевидной необходимости сохранения поступившего сообщения,
    в задании оговорено, что у сообщения должен быть признак "прочитано",
    когда сообщение прочитано всеми участниками чата или группы.
    Помимо этого, должен быть REST-эндпоинт для получения истории сообщений
    по id чата, соответственно, такой метод у нас тоже должен быть.
    Чтобы не перегрузить память большим количеством сообщений, реализуем
    также обработку параметров limit и offset.
    """

    @abstractmethod
    async def save(self, message: Message) -> Message:
        pass

    @abstractmethod
    async def mark_as_read(self, message_id: int) -> None:
        pass

    @abstractmethod
    async def get_by_chat_id(
        self, chat_id: int, limit: int, offset: int
    ) -> list[Message]:
        pass
