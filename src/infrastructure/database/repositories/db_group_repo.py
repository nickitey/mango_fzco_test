from logging import Logger
from typing import Optional

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import LoggerConfigurator
from src.domain.entities import ChatCategory, Group
from src.domain.exceptions import ChatNotFoundException, UserNotFoundException
from src.domain.repositories import GroupRepository
from src.infrastructure.database.models import (ChatModel, GroupModel,
                                                GroupsUsers, UserModel)


class DatabaseGroupRepository(GroupRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._logger: Logger = LoggerConfigurator().get_logger(utc=True)

    async def validate_users(
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

    async def validate_chat(self, chat_id: int):
        query = select(ChatModel).where(ChatModel.id == chat_id)
        async with self.session as session:
            result = await session.execute(query)
        chat = result.scalars().first()
        if not chat:
            err_msg = f"Чат с id {chat_id} не существует"
            self._logger.exception(err_msg)
            raise ChatNotFoundException(err_msg)
        if chat.category == ChatCategory.PRIVATE:
            err_msg = (
                f"Публичный чат с id {chat_id} не существует. Создать "
                "группу на основе приватного чата нельзя."
            )
            self._logger.exception(err_msg)
            raise ChatNotFoundException(err_msg)

    async def create(self, group: Group) -> Group:
        group_data = vars(group).copy()
        group_data.pop("participants")
        group_model = GroupModel(**group_data)
        async with self.session as session:
            session.add(group_model)
            await session.flush()
            await session.execute(
                insert(GroupsUsers).values(
                    [
                        {"group_id": group_model.id, "user_id": user_id}
                        for user_id in group.participants
                    ]
                )
            )
            await session.commit()
            await session.refresh(group_model)
        group.id = group_model.id
        return group

    async def get_by_group_id(self, group_id: int) -> Optional[Group]:
        query = select(GroupModel).where(GroupModel.id == group_id)
        async with self.session as session:
            result = await session.execute(query)
        db_group = result.scalar_one_or_none()
        if db_group is None:
            return None
        db_group_dump = vars(db_group)
        db_group_dump.pop("_sa_instance_state")
        return Group(**db_group_dump)

    async def get_by_chat_id(self, chat_id: int) -> Optional[Group]:
        query = (
            select(GroupModel)
            .where(GroupModel.chat_id == chat_id)
            .options(selectinload(GroupModel.participants))
        )
        async with self.session as session:
            result = await session.execute(query)
        db_group = result.scalar_one_or_none()
        if db_group is None:
            return None
        return Group(**db_group.to_dict())
