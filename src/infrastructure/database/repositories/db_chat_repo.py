from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Chat
from src.domain.repositories import ChatRepository
from src.infrastructure.database.models import ChatModel


class DatabaseChatRepository(ChatRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, chat: Chat) -> Chat:
        db_chat = ChatModel(**vars(chat))
        self.session.add(db_chat)
        await self.session.commit()
        return chat

    async def get_by_id(self, chat_id: int) -> Optional[Chat]:
        query = select(ChatModel).where(ChatModel.id == chat_id)
        result = await self.session.execute(query)
        db_chat = result.scalar_one_or_none()
        db_chat_dump = vars(db_chat)
        db_chat_dump.pop("_sa_instance_state")
        return Chat(**db_chat_dump) if db_chat else None
