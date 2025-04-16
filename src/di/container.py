import redis.asyncio as redis
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from src.application.services.ws_manager import WebSocketManager
from src.application.usecases import (CreateChatUseCase, CreateGroupUseCase,
                                      CreateUserUseCase, GetChatHistoryUseCase,
                                      SendMessageUseCase)
from src.config import Settings
from src.domain.repositories import (ChatRepository, GroupRepository,
                                     MessageRepository, UserRepository)
from src.infrastructure.database.repositories import (
    DatabaseChatRepository, DatabaseGroupRepository, DatabaseMessageRepository,
    DatabaseUserRepository)


class AppProvider(Provider):
    @provide(scope=Scope.APP)
    def get_config(self) -> Settings:
        return Settings()

    @provide(scope=Scope.SESSION)
    async def get_db_session(
        self, settings: Settings
    ) -> async_sessionmaker[AsyncSession]:
        engine = create_async_engine(settings.database.DB_URL)
        return async_sessionmaker(engine, expire_on_commit=False)

    @provide(scope=Scope.SESSION)
    def get_message_repository(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> MessageRepository:
        return DatabaseMessageRepository(session_maker())

    @provide(scope=Scope.SESSION)
    def get_user_repository(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> UserRepository:
        return DatabaseUserRepository(session_maker())

    @provide(scope=Scope.SESSION)
    def get_chat_repository(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> ChatRepository:
        return DatabaseChatRepository(session_maker())

    @provide(scope=Scope.SESSION)
    def get_group_repository(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> GroupRepository:
        return DatabaseGroupRepository(session_maker())

    @provide(scope=Scope.APP)
    def get_websocket_manager(self) -> WebSocketManager:
        return WebSocketManager()

    @provide(scope=Scope.APP)
    def get_redis_client(self, settings: Settings) -> redis.Redis:
        return redis.Redis(
            host=settings.redis.REDIS_HOST,
            port=settings.redis.REDIS_PORT,
            username=settings.redis.REDIS_USER,
            password=settings.redis.REDIS_PASSWORD,
        )

    @provide(scope=Scope.SESSION)
    def get_send_message_use_case(
        self,
        message_repo: MessageRepository,
        chat_repo: ChatRepository,
        user_repo: UserRepository,
        ws_manager: WebSocketManager,
        redis_client: redis.Redis,
    ) -> SendMessageUseCase:
        return SendMessageUseCase(
            message_repo=message_repo,
            chat_repo=chat_repo,
            user_repo=user_repo,
            ws_manager=ws_manager,
            redis_client=redis_client,
        )

    @provide(scope=Scope.REQUEST)
    def get_chat_history_use_case(
        self, message_repo: MessageRepository, chat_repo: ChatRepository
    ) -> GetChatHistoryUseCase:
        return GetChatHistoryUseCase(message_repo, chat_repo)

    @provide(scope=Scope.REQUEST)
    def get_create_user_usecase(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> CreateUserUseCase:
        return CreateUserUseCase(session_maker())

    @provide(scope=Scope.REQUEST)
    def get_create_chat_usecase(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> CreateChatUseCase:
        return CreateChatUseCase(session_maker())

    @provide(scope=Scope.REQUEST)
    def get_create_group_usecase(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> CreateGroupUseCase:
        return CreateGroupUseCase(session_maker())
