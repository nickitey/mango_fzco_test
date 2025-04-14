from src.domain.repositories import MessageRepository, ChatRepository
from src.domain.exceptions import ChatNotFoundException
from src.application.dtos.message_dto import MessageDTO


class GetChatHistoryUseCase:
    def __init__(self, message_repo: MessageRepository, chat_repo: ChatRepository):
        self.message_repo = message_repo
        self.chat_repo = chat_repo

    async def execute(self, chat_id: int, limit: int = 50, offset: int = 0) -> list[MessageDTO]:
        chat = await self.chat_repo.get_by_id(chat_id)
        if not chat:
            raise ChatNotFoundException("Чат с данным идентификатором отсутствует.")

        messages = await self.message_repo.get_by_chat_id(chat_id, limit, offset)
        return [MessageDTO(**vars(msg)) for msg in messages]
