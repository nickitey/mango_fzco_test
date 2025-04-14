from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import User
from src.domain.repositories import UserRepository
from src.infrastructure.database.models import UserModel


class DatabaseUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        db_user = User(**vars(user))
        self.session.add(db_user)
        await self.session.commit()
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        query = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(query)
        db_user = result.scalar_one_or_none()
        return User(**vars(db_user)) if db_user else None
