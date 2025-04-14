from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Group
from src.domain.repositories import GroupRepository
from src.infrastructure.database.models import GroupModel


class DatabaseGroupRepository(GroupRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, group: Group) -> Group:
        db_group = GroupModel(**vars(group))
        self.session.add(db_group)
        await self.session.commit()
        return group

    async def get_by_group_id(self, group_id: int) -> Optional[Group]:
        query = select(GroupModel).where(GroupModel.id == group_id)
        result = await self.session.execute(query)
        db_group = result.scalar_one_or_none()
        return Group(**vars(db_group)) if db_group else None

    async def get_by_chat_id(self, chat_id: int) -> Optional[Group]:
        query = select(GroupModel).where(GroupModel.chat_id == chat_id)
        result = await self.session.execute(query)
        db_group = result.scalar_one_or_none()
        return Group(**vars(db_group)) if db_group else None
