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
        async with self.session as session:
            session.add(db_message)
            await session.commit()
            await session.refresh(db_message)
        message.id = str(db_message.id)
        return message

    async def get_by_id(self, message_id: str) -> Message | None:
        query = select(MessageModel).where(MessageModel.id == message_id)
        async with self.session as session:
            result = await session.execute(query)
        message = result.scalar_one_or_none()
        if message is None:
            return None
        message_dump = vars(message)
        message_dump.pop("_sa_instance_state")
        return Message(**message_dump)

    async def get_by_chat_id(
        self, chat_id: int, limit: int, offset: int
    ) -> list[Message]:
        query = (
            select(MessageModel)
            .where(MessageModel.chat_id == chat_id)
            .order_by(MessageModel.timestamp)
            .limit(limit)
            .offset(offset)
        )
        async with self.session as session:
            result = await session.execute(query)
        messages = result.scalars().all()
        return [
            Message(
                **{
                    key: value
                    for key, value in vars(m).items()
                    if key != "_sa_instance_state"
                }
            )
            for m in messages
        ]

    async def mark_as_read(self, message_id: str) -> None:
        query = select(MessageModel).where(MessageModel.id == message_id)
        async with self.session as session:
            result = await session.execute(query)
            message = result.scalar_one()
            message.is_read = True
            await session.commit()
