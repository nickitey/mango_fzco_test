from enum import Enum

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogfileTTLMeasure(Enum):
    SECONDS = "S"
    MINUTES = "M"
    HOURS = "H"
    DAYS = "D"


class AppConfig(BaseModel):
    LOGGING_LEVEL: str
    LOGFILE_TTL_MEASURE: LogfileTTLMeasure
    LOGFILE_TTL: int


class AppSecurity(BaseModel):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int


class DatabaseSettings(BaseModel):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @property
    def DB_URL(self):
        return "postgresql+psycopg://{}:{}@{}:{}/{}".format(
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST,
            self.POSTGRES_PORT,
            self.POSTGRES_DB,
        )


class RedisSettings(BaseModel):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USER: str
    REDIS_PASSWORD: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__", env_file=".env", extra="ignore"
    )

    app: AppConfig
    auth: AppSecurity
    database: DatabaseSettings
    redis: RedisSettings
