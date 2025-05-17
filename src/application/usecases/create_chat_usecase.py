from src.domain.entities import Chat, ChatCategory
from src.domain.repositories import ChatRepository


class CreateChatUseCase:
    def __init__(self, chat_repo: ChatRepository):
        self.chat_repo = chat_repo

    async def execute(
        self, name: str, category: ChatCategory, participant_ids: list[int]
    ) -> Chat:
        # Проверим существование пользователей, которых нам необходимо
        # добавить в чат
        await self.chat_repo.validate_users(participant_ids)

        chat = Chat(name=name, category=category, participants=participant_ids)
        await self.chat_repo.create(chat)
        return chat
