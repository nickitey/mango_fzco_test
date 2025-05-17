from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import LoggerConfigurator
from src.domain.entities import ChatCategory, Group
from src.domain.exceptions import ChatNotFoundException, UserNotFoundException
from src.domain.repositories import GroupRepository
from src.infrastructure.database.models import (ChatModel, GroupModel,
                                                GroupsUsers, UserModel)


class CreateGroupUseCase:
    def __init__(self, group_repo: GroupRepository):
        self.group_repo = group_repo

    async def execute(
        self,
        name: str,
        chat_id: int,
        creator_id: int,
        participant_ids: list[int],
    ) -> Group:
        # Проверим на наличие всех пользователей
        await self.group_repo.validate_users(participant_ids, creator_id)

        # Проверим, что чат для группы существует и он не приватный
        await self.group_repo.validate_chat(chat_id)

        group = Group(
            name=name,
            chat_id=chat_id,
            creator=creator_id,
            participants=participant_ids,
        )
        await self.group_repo.create(group)
        return group
