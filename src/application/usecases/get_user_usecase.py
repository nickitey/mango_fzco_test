from src.domain.entities import User
from src.domain.repositories import UserRepository


class GetUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self, username: str) -> User | None:
        return await self.user_repo.get_by_username(username)
