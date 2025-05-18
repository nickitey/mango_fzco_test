import os
import typing as t
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import LoggerConfigurator
from src.di import create_container
from src.presentation.api import auth_router, crud_router, hist_router
from src.presentation.websockets import router as ws_router

logger = LoggerConfigurator().get_logger(utc=True)


@asynccontextmanager
async def lifespan(app: FastAPI) -> t.AsyncGenerator[None, None]:
    yield
    await app.state.dishka_container.close()


app = FastAPI(
    title="Тестовое приложение для WinDI Tech",
    description="Приложение, реализующее чат на вебсокетах с историей сообщений",
    lifespan=lifespan,
    logger=logger,
)

container = create_container()
setup_dishka(container, app)

if os.getenv("DEBUG").lower() == "true":
    # Если мы в дебаг-режиме, отключим CORS, чтобы браузер не ругался.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(ws_router)
app.include_router(auth_router)
app.include_router(hist_router)
app.include_router(crud_router)
