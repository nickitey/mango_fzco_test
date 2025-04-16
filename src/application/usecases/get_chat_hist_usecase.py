from src.application.dtos import MessageDTO
from src.config import LoggerConfigurator
from src.domain.exceptions import ChatNotFoundException
from src.domain.repositories import ChatRepository, MessageRepository


class GetChatHistoryUseCase:
    def __init__(
        self, message_repo: MessageRepository, chat_repo: ChatRepository
    ):
        self.message_repo = message_repo
        self.chat_repo = chat_repo
        self._logger = LoggerConfigurator().get_logger(utc=True)

    async def execute(
        self, chat_id: int, limit: int = 50, offset: int = 0
    ) -> list[MessageDTO]:
        # Проверка, что чат, для которого запрошена история, существует
        chat = await self.chat_repo.get_by_id(chat_id)
        if not chat:
            err_msg = f"Чат с идентификатором {chat_id} не существует."
            self._logger.exception(err_msg)
            raise ChatNotFoundException(err_msg)

        messages = await self.message_repo.get_by_chat_id(
            chat_id, limit, offset
        )
        return [MessageDTO(**vars(msg)) for msg in messages]
