from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from src.application.usecases import (CreateChatUseCase, CreateGroupUseCase,
                                      CreateUserUseCase)
from src.config.logging import LoggerConfigurator
from src.domain.exceptions import UserNotUniqueException
from src.presentation.schemas.requests import (ChatCreate, GroupCreate,
                                               UserCreate)

logger = LoggerConfigurator().get_logger(utc=True)
router = APIRouter(prefix="/create")


@router.post("/user")
@inject
async def create_user(
    data: UserCreate, use_case: FromDishka[CreateUserUseCase] = None
):
    """
    Валидация уникальности пользователя по имени и email.
    В SQLAlchemy при нарушении ограничения возбуждается исключение IntegrityError.
    Но оно может объединять слишком много причин для возбуждения такой ошибки,
    тогда как у адаптера psycopg, поверх которого работает алхимия, есть класс
    ошибки специально посвященный нарушению ограничения уникальности.
    Поэтому мы перехватываем ограничение SQLAlchemy, проверяем, что если
    оно произошло от ограничения psycopg, значит имело место нарушение
    ограничения, ответ один.
    Если возника в общем какая-то ошибка, ответ другой.
    """
    try:
        user = await use_case.execute(data.name, data.email, data.password)
    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolation):
            err_msg = (
                "Пользователь с такими именем или адресом почты уже"
                "существует"
            )
            logger.exception(err_msg)
            raise UserNotUniqueException(
                detail=err_msg,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        err_msg = "Возникла ошибка при создании пользователя: "
        logger.exception(err_msg + e)
        raise HTTPException(
            detail=str(e), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        ) from e

    return JSONResponse(
        {"id": user.id, "name": user.name, "email": user.email}
    )


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
