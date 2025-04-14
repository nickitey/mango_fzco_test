# Основной файл приложения (main.py)
from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka
from src.presentation.api import router as api_router
from src.presentation.websockets import router as ws_router
from src.di import create_container

app = FastAPI(title="Тестовое приложение для WinDI Tech")

# Подключение роутеров
app.include_router(ws_router)
app.include_router(api_router)
app.include_router(ws_router)

# Настройка DI
container = create_container()
setup_dishka(container, app)
