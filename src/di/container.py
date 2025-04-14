import redis.asyncio as redis
from dishka import Provider, Scope, provide
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from src.application.services.ws_manager import WebSocketManager
from src.config import Settings
from src.domain.repositories import (ChatRepository, GroupRepository,
                                     MessageRepository, UserRepository)
from src.infrastructure.database.repositories import (
    DatabaseChatRepository, DatabaseGroupRepository, DatabaseMessageRepository,
    DatabaseUserRepository)


class AppProvider(Provider):
    @provide(scope=Scope.APP)
    def get_config(self) -> Settings:
        load_dotenv(find_dotenv())
        return Settings()

    @provide(scope=Scope.REQUEST)
    async def get_db_session(
        self, settings: Settings
    ) -> async_sessionmaker[AsyncSession]:
        db_url = "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            settings.database.POSTGRES_HOST,
            settings.database.POSTGRES_PORT,
            settings.database.POSTGRES_USER,
            settings.database.POSTGRES_PASSWORD,
            settings.database.POSTGRES_DB,
        )
        engine = create_async_engine(db_url)
        return async_sessionmaker(engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    def get_message_repository(
        self, session: AsyncSession
    ) -> MessageRepository:
        return DatabaseMessageRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_user_repository(self, session: AsyncSession) -> UserRepository:
        return DatabaseUserRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_chat_repository(self, session: AsyncSession) -> ChatRepository:
        return DatabaseChatRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_group_repository(self, session: AsyncSession) -> GroupRepository:
        return DatabaseGroupRepository(session)

    @provide(scope=Scope.APP)
    def get_websocket_manager(
        self, group_repo: GroupRepository
    ) -> WebSocketManager:
        return WebSocketManager(group_repo)

    @provide(scope=Scope.APP)
    def get_redis_client(self, settings: Settings) -> redis.Redis:
        return redis.Redis(
            host=settings.redis.REDIS_HOST,
            port=settings.redis.REDIS_PORT,
            username=settings.redis.REDIS_USER,
            password=settings.redis.REDIS_PASSWORD,
        )
