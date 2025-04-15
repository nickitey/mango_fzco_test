from datetime import datetime, timezone

import redis.asyncio as redis

from src.application.services import WebSocketManager
from src.domain.entities.message import Message
from src.domain.exceptions import (ChatNotFoundException,
                                   DuplicateMessageException,
                                   UserNotFoundException)
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
        # Проверка дублирования
        cache_msg_key = f"msg:{message_id}"
        if await self.redis_client.get(cache_msg_key):
            raise DuplicateMessageException("Данное сообщение уже обработано")

        # Проверка существования чата и отправителя
        chat = await self.chat_repo.get_by_id(chat_id)
        if not chat:
            raise ChatNotFoundException("Запрошенный чат не существует")

        user = await self.user_repo.get_by_id(sender_id)
        if not user:
            raise UserNotFoundException(
                "Запрошенный пользователь не существует"
            )

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

        # Рассылка через WebSocket
        await self.ws_manager.broadcast(message, chat_id)

        return message
