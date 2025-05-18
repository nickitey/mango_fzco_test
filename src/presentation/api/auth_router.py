from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from src.application.services import AuthService
from src.presentation.schemas.auth_requests import RefreshRequest, TokenRequest

router = APIRouter(prefix="/auth")


@router.post("/login")
@inject
async def login(
    data: TokenRequest, auth_service: FromDishka[AuthService] = None
):
    tokens = await auth_service.authenticate(data.username, data.password)
    if not tokens:
        raise HTTPException(
            status_code=401, detail="Неправильные логин или пароль."
        )
    return JSONResponse(tokens)


@router.post("/refresh")
@inject
def refresh_token(
    data: RefreshRequest, auth_service: FromDishka[AuthService] = None
):
    try:
        access_token = auth_service.refresh_access_token(data.refresh_token)
        return JSONResponse({"access_token": access_token})
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="refresh_token невалиден. Авторизуйтесь заново.",
        )
