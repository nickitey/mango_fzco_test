from fastapi import WebSocket

from src.domain.entities import ChatCategory, Message
from src.domain.exceptions import (GroupNotFoundException,
                                   MessageNotFoundException)
from src.domain.repositories import (ChatRepository, GroupRepository,
                                     MessageRepository)


class WebSocketManager:
    """
    Класс-менеджер сокетов. Реализует четыре метода: подключение сокета
    с пользователем, его отключение, рассылку сообщений и сбор подтверждений
    о прочтении.
    """

    def __init__(self):
        self.connections: dict[int, WebSocket] = {}
        self.read_confirmations: dict[str, set[int]] = {}

    async def connect(
        self, user_id: int, websocket: WebSocket, group_repo: GroupRepository
    ):
        await websocket.accept()
        self.group_repo = group_repo
        self.connections[user_id] = websocket

    async def disconnect(self, user_id: int):
        self.connections.pop(user_id, None)

    async def send_private_message(self, message: Message, receiver_id: int):
        if receiver_id in self.connections:
            await self.connections[receiver_id].send_json(
                {
                    "id": message.id,
                    "chat_id": message.chat_id,
                    "sender_id": message.sender_id,
                    "text": message.text,
                    "timestamp": message.timestamp.isoformat(),
                    "is_read": message.is_read,
                }
            )

    async def broadcast(self, message: Message, chat_id: int):
        group = await self.group_repo.get_by_group_id(chat_id)
        if not group:
            raise GroupNotFoundException(f"Группа с {chat_id} не существует.")

        for user_id in group.participants:
            if user_id in self.connections:
                await self.connections[user_id].send_json(
                    {
                        "id": message.id,
                        "chat_id": message.chat_id,
                        "sender_id": message.sender_id,
                        "text": message.text,
                        "timestamp": message.timestamp.isoformat(),
                        "is_read": message.is_read,
                    }
                )

    async def confirm_read(
        self,
        message_id: str,
        chat_id: int,
        user_id: int,
        group_repo: GroupRepository,
        chat_repo: ChatRepository,
        message_repo: MessageRepository,
    ) -> bool:
        """
        Обрабатывает подтверждение прочтения от пользователя.
        Возвращает True, если все участники (кроме отправителя) прочитали сообщение.
        """

        # Получаем чат и определяем, приватный он или публичный
        chat = await chat_repo.get_by_id(chat_id)
        if chat.category == ChatCategory.PRIVATE:
            # Если чат приватный, очевидно, что, раз мы тут оказались, значит
            # второй собеседник (его клиент) прислал подтверждение прочтения.
            # Дополнительна логика обработки данного поведения не требуется.
            return True

        return await self._confirm_read_in_group(
            message_id, user_id, message_repo, group_repo
        )

    async def _confirm_read_in_group(
        self,
        message_id: str,
        user_id: int,
        message_repo: MessageRepository,
        group_repo: GroupRepository,
    ):
        if message_id not in self.read_confirmations:
            # Для каждого сообщения создаем временное множество прочитавших
            # его адресатов
            self.read_confirmations[message_id] = set()
        self.read_confirmations[message_id].add(user_id)

        message = await message_repo.get_by_id(message_id)
        if not message:
            raise MessageNotFoundException(
                f"Сообщение {message_id} не найдено"
            )

        group = await group_repo.get_by_group_id(message.chat_id)
        if not group:
            raise GroupNotFoundException(
                f"Группа для chat_id={message.chat_id} не найдена"
            )

        # Проверяем, все ли участники (кроме отправителя) прочитали
        participants_except_sender = set(group.participants) - {
            message.sender_id
        }
        read_by = self.read_confirmations[message_id]
        all_read = participants_except_sender.issubset(read_by)

        if all_read:
            # Очищаем временное состояние
            del self.read_confirmations[message_id]
        return all_read
