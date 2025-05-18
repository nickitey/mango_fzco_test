from abc import ABC, abstractmethod
from datetime import timedelta


class AbstractJWTService(ABC):
    @abstractmethod
    def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        pass

    @abstractmethod
    def create_refresh_token(self, data: dict) -> str:
        pass

    @abstractmethod
    def verify_token(self, token: str) -> dict:
        pass
