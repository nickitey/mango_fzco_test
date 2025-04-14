from fastapi import WebSocket

from src.domain.entities import Message
from src.domain.exceptions import GroupNotFoundException
from src.domain.repositories import GroupRepository


class WebSocketManager:
    """
    Класс-менеджер сокетов. Реализует три метода: подключение сокета
    с пользователем, его отключение, а также рассылку сообщений
    всем
    """

    def __init__(self):
        self.connections: dict[int, WebSocket] = {}

    async def connect(
        self, user_id: int, websocket: WebSocket, group_repo: GroupRepository
    ):
        await websocket.accept()
        self.group_repo = group_repo
        self.connections[user_id] = websocket

    async def disconnect(self, user_id: int):
        self.connections.pop(user_id, None)

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
