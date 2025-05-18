from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from fastapi.params import Query
from jwt import DecodeError, ExpiredSignatureError, InvalidTokenError

from src.application.services import WebSocketManager
from src.application.usecases import SendMessageUseCase
from src.config import LoggerConfigurator
from src.domain.repositories import (ChatRepository, GroupRepository,
                                     MessageRepository)
from src.infrastructure.security import JWTService

router = APIRouter()


@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: int,
    token: str,
):
    """
    Заметки для себя: Dishka отвратительно работает с вебсокетами. Работе с ними
    в документации в принципе посвящен один короткий абзац, из которого следует,
    что зависимости с контекстом (scope) REQUEST (на уровне запроса)
    здесь работают как-то так себе.
    О чем автор умолчал - о том, что *все* зависимости здесь работают как-то так
    себе в силу длительности соединения вебсокета. Поэтому целым приключением
    оказалось сделать один менеджер вебсокетов для нескольких соединений,
    так, чтобы несколько пользователей могли подключаться и общаться между
    собой, т.е. чтобы их соединения обслуживались одним менеджером.
    Dishka категорически не может стыковать контейнеры с зависимостями, если
    у них разные scope.
    В результате пришлось сделать несколько нелогично, и репозиторий для работы
    с группами перемещать в метод-коннектор менеджера - просто потому что этот
    репозиторий использует для инициализации объект сессии SQLAlchemy, а создать
    этот объект с контекстом на все приложение не получится - СУБД не держит
    длинные соединения, запросы должны быть атомарными, завершаться, когда
    соединение завершено (а в идеале еще раньше).
    Чего также категорически нельзя делать в случае вебсокетов и dishka:
    1) использовать прямую инъекцию через декоратор @inject, dishka просто
    будет обрывать все соединения из-за того, что не сможет разобраться
    с зависимостями, возвращать молча ошибку соединение 403, и это очень
    неочевидно, что эта 403 именно от dishka;
    2) использовать явную передачу в параметры обработчика AsyncContainer,
    поскольку FastAPI будет неистово хотеть провалидировать этот объект
    с помощью Pydantic и потерпит сокрушительное фиаско;
    3) использовать встроенный инъектор зависимостей FastAPI - Depends,
    потому что dishka не умеет работать с вебсокетами как с HTTP-запросами,
    контекст REQUEST не создается, а значит ничего не получится.

    Как все же получить свои зависимости в обработчике вебсокетов?
    Ну, и сложно, и просто: нужно зайти с обратной стороны, так сказать,
    с тыла.
    В точке входа создается асинхронный контейнер с зависимостями, а затем
    он связывается с приложением FastAPI.
    Соответственно, на уровне с самой широкой областью видимости для приложения,
    то есть на уровне самого экземпляра FastAPI контейнер становится доступен.
    Более того, он становится одним из атрибутов самого приложения.
    А вебсокет, который обрабатывается данным хэдлером, хранит в себе информацию
    об объекте, который его обслуживает. Поэтому, внутри хэндлера доступен
    вебсокет, внутри вебсокета доступно приложение, внутри приложения доступен
    контейнер с зависимостями.
    """
    container = websocket.app.state.dishka_container
    async with container() as request_container:
        ws_manager = await request_container.get(WebSocketManager)
        send_message_usecase = await request_container.get(SendMessageUseCase)
        group_repo = await request_container.get(GroupRepository)
        message_repo = await request_container.get(MessageRepository)
        chat_repo = await request_container.get(ChatRepository)
        jwt_service = await request_container.get(JWTService)

    logger = LoggerConfigurator().get_logger(utc=True)
    # Проверка JWT-токена.
    # О том, почему токен передается в параметрах запроса,
    # есть хорошая статья: https://habr.com/ru/articles/790272
    try:
        payload = jwt_service.verify_token(token)
        user_id = int(payload["sub"])
    except (ValueError, ExpiredSignatureError, DecodeError, InvalidTokenError):
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Ошибка валидации токена.",
        )
        logger.info(
            f"В чат #{chat_id} была попытка входа пользователя без "
            "действующего JWT."
        )
        return

    # Проверим, является ли данный пользователь участником этого чата
    if not await chat_repo.check_chat_participant(chat_id, user_id):
        logger.info(
            f"К чату #{chat_id} пытался подключиться пользователь #{user_id}, "
            "который не является участником этого чата. "
            "В установлении соединения отказано."
        )
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Пользователь не является участником данного чата.",
        )
        return

    try:
        await ws_manager.connect(user_id, websocket, group_repo)
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type", "message")

            if message_type == "message":
                text = data["text"]
                message_id = str(uuid4())
                await send_message_usecase.execute(
                    chat_id, user_id, text, message_id
                )

            elif message_type == "read":
                message_id = data["message_id"]
                all_read = await ws_manager.confirm_read(
                    message_id,
                    chat_id,
                    user_id,
                    group_repo,
                    chat_repo,
                    message_repo,
                )
                if all_read is True:
                    await message_repo.mark_as_read(message_id)
            else:
                await websocket.close(
                    code=status.WS_1003_UNSUPPORTED_DATA,
                    reason="Неподдерживаемый формат сообщения",
                )
    except WebSocketDisconnect:
        logger.info(f"Клиент с user_id {user_id} покинул чат")
    except Exception as e:
        logger.exception(
            f"Соединение с пользователем с user_id {user_id} прервалось "
            f"с ошибкой {e}"
        )
    finally:
        await ws_manager.disconnect(user_id, websocket)
