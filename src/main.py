import logging
import typing as t
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.config import Settings
from src.di import create_container
from src.domain.entities import ChatCategory
from src.infrastructure.database.models import ChatModel, GroupModel, UserModel
from src.infrastructure.database.models.base import Base
from src.presentation.api import hist_router, crud_router
from src.presentation.websockets import router as ws_router

logger = logging.getLogger()

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI) -> t.AsyncGenerator[None, None]:
    logger.info("Инициализация базы данных")

    # Создаем движок и сессию
    engine = create_async_engine(settings.database.DB_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы базы данных созданы")

    # Добавляем тестовые данные
    async with async_session() as session:
        async with session.begin():
            # Проверяем, есть ли пользователи
            result = await session.execute(select(UserModel).where(UserModel.id.in_([1, 2, 3])))
            users = result.scalars().all()

            if not users:
                logger.warning("Добавление тестовых пользователей")
                await session.execute(insert(UserModel).values([
                    {"id": 1, "name": "User1", "email": "user1@example.com", "password_hash": "hash1"},
                    {"id": 2, "name": "User2", "email": "user2@example.com", "password_hash": "hash2"},
                    {"id": 3, "name": "User3", "email": "user3@example.com", "password_hash": "hash3"},
                ]))

                user1 = await session.get(UserModel, 1)
                user2 = await session.get(UserModel, 2)
                user3 = await session.get(UserModel, 3)

                # Добавляем тестовые чаты, приватный и публичный
                session.add(
                    ChatModel(
                        id=1, name="Test Chat1", category=ChatCategory.PRIVATE,
                        participants=[user1, user2]
                    )
                )
                session.add(
                    ChatModel(
                        id=2, name="Test Chat2", category=ChatCategory.PUBLIC,
                        participants=[user1, user2, user3]
                    )
                )

                # Добавляем тестовую группу
                session.add(
                    GroupModel(
                        id=1, chat_id=2, name="Test Group", creator=1,
                        participants=[user1, user2, user3]
                    )
                )

                await session.commit()
                logger.info("Тестовые данные добавлены")
            else:
                logger.warning("Тестовые пользователи уже существуют")

    logger.info("Инициализация завершена")
    yield
    await app.state.dishka_container.close()


app = FastAPI(
    title="Тестовое приложение для WinDI Tech",
    description="Приложение, реализующее чат на вебсокетах с историей сообщений",
    lifespan=lifespan
)

container = create_container()
setup_dishka(container, app)


app.include_router(ws_router)
app.include_router(hist_router)
app.include_router(crud_router)
