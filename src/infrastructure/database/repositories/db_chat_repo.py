from logging import Logger
from typing import NoReturn

from sqlalchemy import exists, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import LoggerConfigurator
from src.domain.entities import Chat, User
from src.domain.exceptions import UserNotFoundException
from src.domain.repositories import ChatRepository
from src.infrastructure.database.models import ChatModel, ChatsUsers, UserModel


class DatabaseChatRepository(ChatRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._logger: Logger = LoggerConfigurator().get_logger(utc=True)

    async def validate_users(
        self, participant_ids: list[int]
    ) -> None | NoReturn:
        query = select(UserModel).where(UserModel.id.in_(participant_ids))
        async with self.session as session:
            result = await session.execute(query)
        users = result.scalars().all()
        users_ids = {user.id for user in users}
        for participant_id in participant_ids:
            if participant_id not in users_ids:
                err_msg = f"Пользователь с id {participant_id} не существует"
                self._logger.exception(err_msg)
                raise UserNotFoundException(err_msg)

    async def create(self, chat: Chat) -> Chat:
        chat_data = vars(chat).copy()
        chat_data.pop("participants")
        db_chat = ChatModel(**chat_data)
        async with self.session as session:
            session.add(db_chat)
            await session.flush()
            await session.execute(
                insert(ChatsUsers).values(
                    [
                        {"chat_id": db_chat.id, "user_id": user_id}
                        for user_id in chat.participants
                    ]
                )
            )
            await session.commit()
        chat.id = db_chat.id
        return chat

    async def get_by_id(self, chat_id: int) -> Chat | None:
        query = (
            select(ChatModel)
            .where(ChatModel.id == chat_id)
            .options(selectinload(ChatModel.participants))
        )
        async with self.session as session:
            result = await session.execute(query)
        db_chat = result.scalar_one_or_none()
        if db_chat is None:
            return None
        db_chat_dump = vars(db_chat)
        db_chat_dump.pop("_sa_instance_state")
        return Chat(**db_chat_dump)

    async def get_chat_participants(self, chat_id: int) -> list[User | None]:
        query = (
            select(ChatModel)
            .where(ChatModel.id == chat_id)
            .options(selectinload(ChatModel.participants))
        )
        async with self.session as session:
            result = await session.execute(query)
        chat = result.scalars().one()
        return [
            User(
                **{
                    key: value
                    for key, value in vars(user).items()
                    if key != "_sa_instance_state"
                }
            )
            for user in chat.participants
        ]

    async def check_chat_participant(self, chat_id: int, user_id: int) -> bool:
        query = exists().where(
            (ChatsUsers.chat_id == chat_id) & (ChatsUsers.user_id == user_id)
        )
        async with self.session as session:
            result = await session.execute(select(query))
        return result.scalar()
