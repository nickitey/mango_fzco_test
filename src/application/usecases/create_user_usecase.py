from sqlalchemy.ext.asyncio import AsyncSession

from src.config import hash_password
from src.infrastructure.database.models import UserModel


class CreateUserUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(self, name: str, email: str, password: str) -> UserModel:
        password_hash = hash_password(password)
        user = UserModel(name=name, email=email, password_hash=password_hash)
        async with self.session as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user
