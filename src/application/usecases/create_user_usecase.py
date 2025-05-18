from src.domain.entities import User
from src.domain.repositories import UserRepository


class CreateUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, name: str, email: str, password: str) -> User:
        user = User.create_with_password(
            name=name, email=email, password=password
        )
        return await self.user_repo.create(user)
