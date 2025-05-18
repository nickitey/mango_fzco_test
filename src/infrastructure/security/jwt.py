from datetime import datetime, timedelta, timezone

import jwt

from src.config import Settings
from src.domain.services import AbstractJWTService


class JWTService(AbstractJWTService):
    def __init__(self, settings: Settings):
        self.secret_key = settings.auth.SECRET_KEY
        self.algorithm = settings.auth.ALGORITHM
        self.access_token_exp = settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_exp = settings.auth.REFRESH_TOKEN_EXPIRE_DAYS

    def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(tz=timezone.utc) + (
            expires_delta or timedelta(minutes=self.access_token_exp)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, data: dict) -> str:
        expire = datetime.now(tz=timezone.utc) + timedelta(
            days=self.refresh_token_exp
        )
        to_encode = data.copy()
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
