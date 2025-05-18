from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from src.application.dtos import MessageDTO
from src.application.usecases import GetChatHistoryUseCase

router = APIRouter(prefix="/history")


@router.get(
    "/{chat_id}",
    response_model=list[MessageDTO],
    openapi_extra={"include_in_schema": True},
)
@inject
async def get_history(
    chat_id: int,
    limit: int = 50,
    offset: int = 0,
    use_case: FromDishka[GetChatHistoryUseCase] = None,
):
    return await use_case.execute(chat_id, limit, offset)
