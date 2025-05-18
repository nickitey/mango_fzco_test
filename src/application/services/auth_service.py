from src.domain.repositories import UserRepository
from src.domain.services import AbstractJWTService


class AuthService:
    def __init__(
        self, user_repo: UserRepository, jwt_service: AbstractJWTService
    ):
        self._user_repo = user_repo
        self._jwt_service = jwt_service

    async def authenticate(self, username: str, password: str):
        user = await self._user_repo.get_by_username(username)
        if not user or not user.verify_password(password):
            return None
        payload = {
            "sub": str(user.id),
            "username": user.name,
            "email": user.email,
        }
        return {
            "access_token": self._jwt_service.create_access_token(payload),
            "refresh_token": self._jwt_service.create_refresh_token(payload),
        }

    def refresh_access_token(self, refresh_token: str):
        payload = self._jwt_service.verify_token(refresh_token)
        return self._jwt_service.create_access_token(payload)
