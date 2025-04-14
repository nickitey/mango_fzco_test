from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Message
from src.domain.repositories import MessageRepository
from src.infrastructure.database.models import MessageModel


class DatabaseMessageRepository(MessageRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, message: Message) -> Message:
        db_message = MessageModel(**vars(message))
        self.session.add(db_message)
        await self.session.commit()
        return message

    async def get_by_chat_id(
        self, chat_id: int, limit: int, offset: int
    ) -> List[Message]:
        query = (
            select(MessageModel)
            .where(MessageModel.chat_id == chat_id)
            .order_by(MessageModel.timestamp)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        messages = result.scalars().all()
        return [Message(**vars(m)) for m in messages]

    async def mark_as_read(self, message_id: int) -> None:
        query = select(MessageModel).where(MessageModel.id == message_id)
        result = await self.session.execute(query)
        message = result.scalar_one()
        message.is_read = True
        await self.session.commit()
