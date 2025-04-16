from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import LoggerConfigurator
from src.domain.entities import ChatCategory
from src.domain.exceptions import ChatNotFoundException, UserNotFoundException
from src.infrastructure.database.models import (ChatModel, GroupModel,
                                                GroupsUsers, UserModel)


class CreateGroupUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._logger = LoggerConfigurator().get_logger(utc=True)

    async def _validate_users(
        self, participant_ids: list[int], creator_id: int
    ):
        # Проверим, существует ли такой создатель группы
        creator_found = False

        query = select(UserModel).where(UserModel.id.in_(participant_ids))
        async with self.session as session:
            result = await session.execute(query)
        users = result.scalars().all()
        users_ids = {user.id for user in users}

        for participant_id in participant_ids:
            if participant_id == creator_id:
                creator_found = True
            if participant_id not in users_ids:
                err_msg = f"Пользователь с id {participant_id} не существует"
                self._logger.exception(err_msg)
                raise UserNotFoundException(err_msg)
        if not creator_found:
            err_msg = f"Пользователь с id {creator_id} не существует"
            self._logger.exception(err_msg)
            raise UserNotFoundException(err_msg)

    async def _validate_chat(self, chat_id: int):
        query = select(ChatModel).where(ChatModel.id == chat_id)
        async with self.session as session:
            result = await session.execute(query)
        chat = result.scalars().first()
        if not chat:
            err_msg = f"Чат с id {chat_id} не существует"
            self._logger.exception(err_msg)
            raise ChatNotFoundException(err_msg)
        if chat.category == ChatCategory.PRIVATE:
            err_msg = (f"Публичный чат с id {chat_id} не существует. Создать "
                      "группу на основе приватного чата нельзя.")
            self._logger.exception(err_msg)
            raise ChatNotFoundException(err_msg)

    async def execute(
        self,
        name: str,
        chat_id: int,
        creator_id: int,
        participant_ids: list[int],
    ) -> GroupModel:
        # Проверим на наличие всех пользователей
        await self._validate_users(participant_ids, creator_id)

        # Проверим, что чат для группы существует и он не приватный
        await self._validate_chat(chat_id)

        group = GroupModel(name=name, chat_id=chat_id, creator=creator_id)
        async with self.session as session:
            session.add(group)
            await session.flush()
            await session.execute(
                insert(GroupsUsers).values(
                    [
                        {"group_id": group.id, "user_id": user_id}
                        for user_id in participant_ids
                    ]
                )
            )
            await session.commit()
            await session.refresh(group)
        return group
