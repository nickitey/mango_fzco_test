from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import ChatCategory
from src.domain.exceptions import UserNotFoundException
from src.infrastructure.database.models import ChatModel, ChatsUsers, UserModel


class CreateChatUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _validate_users(self, participant_ids: list[int]):
        query = select(UserModel).where(UserModel.id.in_(participant_ids))
        async with self.session as session:
            result = await session.execute(query)
        users = result.scalars().all()
        users_ids = {user.id for user in users}
        for participant_id in participant_ids:
            if participant_id not in users_ids:
                raise UserNotFoundException(
                    f"Пользователь с id {participant_id} не существует"
                )

    async def execute(
        self, name: str, category: ChatCategory, participant_ids: list[int]
    ) -> ChatModel:
        # Проверим, что пользователи, которых хотят добавить в чат, уже существуют.
        await self._validate_users(participant_ids)

        chat = ChatModel(name=name, category=category)
        async with self.session as session:
            session.add(chat)
            await session.flush()
            await session.execute(
                insert(ChatsUsers).values(
                    [
                        {"chat_id": chat.id, "user_id": user_id}
                        for user_id in participant_ids
                    ]
                )
            )
            await session.commit()
            await session.refresh(chat)
        return chat
