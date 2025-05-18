import asyncio
import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

with open("hs256_secret.key") as secret:
    secret_key = secret.read()

os.environ["AUTH__SECRET_KEY"] = secret_key


from src.config import Settings
from src.domain.entities import Chat, ChatCategory, Group, User
from src.infrastructure.database.repositories import (DatabaseChatRepository,
                                                      DatabaseGroupRepository,
                                                      DatabaseUserRepository)


user1 = User.create_with_password(
    name="User1", email="user1@mail.com", password="password123"
)
user2 = User.create_with_password(
    name="User2", email="user2@mail.com", password="password123"
)
user3 = User.create_with_password(
    name="User3", email="user3@mail.com", password="password123"
)



chat1 = Chat(
    name="some_public_chat", category=ChatCategory.PRIVATE, participants=[1, 2]
)
chat2 = Chat(
    name="some_private_chat",
    category=ChatCategory.PUBLIC,
    participants=[1, 2, 3],
)

group = Group(
    name="some_public_group", creator=2, participants=[1, 2, 3], chat_id=2
)

from pprint import pprint

pprint(vars(user1))
pprint(vars(user2))
pprint(vars(user3))

pprint(vars(chat1))
pprint(vars(chat2))

pprint(vars(group))
#
#
# async_session = async_sessionmaker(
#     create_async_engine(
#         url=Settings().database.DB_URL, echo=True
#     ),
#     expire_on_commit=False
# )
#
# user_repo = DatabaseUserRepository(async_session())
# chat_repo = DatabaseChatRepository(async_session())
# group_repo = DatabaseGroupRepository(async_session())
#
#
# async def main():
#     for user in (user1, user2, user3):
#         await user_repo.create(user)
#
#     for chat in (chat1, chat2):
#         await chat_repo.create(chat)
#
#     await group_repo.create(group)
#
#     print("База наполнена тестовыми данными.")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
