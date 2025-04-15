from datetime import datetime, timezone

import redis.asyncio as redis

from src.application.services import WebSocketManager
from src.domain.entities import ChatCategory, Message
from src.domain.exceptions import (ChatNotFoundException,
                                   DuplicateMessageException)
from src.domain.repositories import (ChatRepository, MessageRepository,
                                     UserRepository)


class SendMessageUseCase:
    def __init__(
        self,
        message_repo: MessageRepository,
        chat_repo: ChatRepository,
        user_repo: UserRepository,
        ws_manager: WebSocketManager,
        redis_client: redis.Redis,
    ):
        self.message_repo = message_repo
        self.chat_repo = chat_repo
        self.user_repo = user_repo
        self.ws_manager = ws_manager
        self.redis_client = redis_client

    async def execute(
        self, chat_id: int, sender_id: int, text: str, message_id: str
    ):
        chat = await self.chat_repo.get_by_id(chat_id)
        if not chat:
            raise ChatNotFoundException("Запрошенный чат не существует")

        if chat.category == ChatCategory.PRIVATE:
            return await self._handle_private_message(
                chat_id, sender_id, text, message_id
            )

        return await self._handle_group_message(
            chat_id, sender_id, text, message_id
        )

    async def _handle_private_message(
        self, chat_id: int, sender_id: int, text: str, message_id: str
    ):
        # Проверка дублирования
        cache_msg_key = f"public_msg:{message_id}"
        if await self.redis_client.get(cache_msg_key):
            raise DuplicateMessageException("Данное сообщение уже обработано")

        participants = await self.chat_repo.get_chat_participants(chat_id)
        receiver_id = next(u.id for u in participants if u.id != sender_id)

        message = Message(
            id=message_id,
            chat_id=chat_id,
            sender_id=sender_id,
            text=text,
            timestamp=datetime.now(timezone.utc),
            is_read=False,
        )
        await self.message_repo.save(message)

        # Сохранение в Redis для предотвращения дублирования
        await self.redis_client.setex(cache_msg_key, 60, "1")

        await self.ws_manager.send_private_message(message, receiver_id)

    async def _handle_group_message(
        self, chat_id: int, sender_id: int, text: str, message_id: str
    ):
        cache_msg_key = f"public_msg:{message_id}"
        if await self.redis_client.get(cache_msg_key):
            raise DuplicateMessageException("Данное сообщение уже обработано")

        # Проверка существования чата и отправителя
        chat = await self.chat_repo.get_by_id(chat_id)
        if not chat:
            raise ChatNotFoundException("Запрошенный чат не существует")

        # Создание и сохранение сообщения
        message = Message(
            id=message_id,
            chat_id=chat_id,
            sender_id=sender_id,
            text=text,
            timestamp=datetime.now(timezone.utc),
            is_read=False,
        )
        await self.message_repo.save(message)

        # Сохранение в Redis для предотвращения дублирования
        await self.redis_client.setex(cache_msg_key, 60, "1")

        await self.ws_manager.broadcast(message, chat_id)
