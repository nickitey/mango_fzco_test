from src.config import hash_password
from src.domain.entities import User
from src.domain.repositories import UserRepository


class CreateUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, name: str, email: str, password: str) -> User:
        password_hash = hash_password(password)
        user = User(name=name, email=email, password_hash=password_hash)
        return await self.user_repo.create(user)
