from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import User
from src.domain.repositories import UserRepository
from src.infrastructure.database.models import UserModel


class DatabaseUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        db_user = UserModel(**vars(user))
        async with self.session as session:
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)
        user.id = db_user.id
        return user

    async def get_by_username(self, username: str) -> User | None:
        query = select(UserModel).where(UserModel.name == username)
        async with self.session as session:
            result = await session.execute(query)
        db_user = result.scalar_one_or_none()
        if db_user is None:
            return None
        db_user_dump = vars(db_user)
        db_user_dump.pop("_sa_instance_state")
        return User(**db_user_dump)
