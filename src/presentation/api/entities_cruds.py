from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.application.usecases import CreateChatUseCase, CreateGroupUseCase, CreateUserUseCase
from src.presentation.schemas.requests import ChatCreate, GroupCreate, UserCreate

router = APIRouter(prefix="/create")


@router.post("/user")
@inject
async def create_user(data: UserCreate, use_case: FromDishka[CreateUserUseCase] = None):
    user = await use_case.execute(data.name, data.email, data.password)
    return JSONResponse({"id": user.id, "name": user.name, "email": user.email})


@router.post("/chat")
@inject
async def create_chat(data: ChatCreate, use_case: FromDishka[CreateChatUseCase] = None):
    chat = await use_case.execute(data.name, data.category, data.participant_ids)
    return JSONResponse({"id": chat.id, "name": chat.name, "category": chat.category.value})


@router.post("/group")
@inject
async def create_group(data: GroupCreate, use_case: FromDishka[CreateGroupUseCase] = None):
    group = await use_case.execute(data.name, data.chat_id, data.creator_id, data.participant_ids)
    return JSONResponse({"id": group.id, "name": group.name})
