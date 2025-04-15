from fastapi import WebSocket

from src.domain.entities import ChatCategory, Message
from src.domain.exceptions import (GroupNotFoundException,
                                   MessageNotFoundException)
from src.domain.repositories import (ChatRepository, GroupRepository,
                                     MessageRepository)


class WebSocketManager:
    """
    Класс-менеджер сокетов. Реализует четыре метода: подключение сокета
    с пользователем, его отключение, рассылку сообщений и сбор подтверждений
    о прочтении.
    """

    def __init__(self):
        self.connections: dict[int, WebSocket] = {}
        self.read_confirmations: dict[str, set[int]] = {}

    async def connect(
        self, user_id: int, websocket: WebSocket, group_repo: GroupRepository
    ):
        await websocket.accept()
        self.group_repo = group_repo
        self.connections[user_id] = websocket

    async def disconnect(self, user_id: int):
        self.connections.pop(user_id, None)

    async def send_private_message(self, message: Message, receiver_id: int):
        if receiver_id in self.connections:
            await self.connections[receiver_id].send_json(
                {
                    "id": message.id,
                    "chat_id": message.chat_id,
                    "sender_id": message.sender_id,
                    "text": message.text,
                    "timestamp": message.timestamp.isoformat(),
                    "is_read": message.is_read,
                }
            )

    async def broadcast(self, message: Message, chat_id: int):
        group = await self.group_repo.get_by_chat_id(chat_id)
        if not group:
            raise GroupNotFoundException(f"Группа с {chat_id} не существует.")

        for user in group.participants:
            if user.id in self.connections and user.id != message.sender_id:
                await self.connections[user.id].send_json(
                    {
                        "id": message.id,
                        "chat_id": message.chat_id,
                        "sender_id": message.sender_id,
                        "text": message.text,
                        "timestamp": message.timestamp.isoformat(),
                        "is_read": message.is_read,
                    }
                )

    async def confirm_read(
        self,
        message_id: str,
        chat_id: int,
        user_id: int,
        group_repo: GroupRepository,
        chat_repo: ChatRepository,
        message_repo: MessageRepository,
    ) -> bool:
        """
        Обрабатывает подтверждение прочтения от пользователя.
        Возвращает True, если все участники (кроме отправителя) прочитали сообщение.
        """

        # Получаем чат и определяем, приватный он или публичный
        chat = await chat_repo.get_by_id(chat_id)
        if chat.category == ChatCategory.PRIVATE:
            # Если чат приватный, очевидно, что, раз мы тут оказались, значит
            # второй собеседник (его клиент) прислал подтверждение прочтения.
            # Дополнительна логика обработки данного поведения не требуется.
            return True

        return await self._confirm_read_in_group(
            message_id, user_id, message_repo, group_repo
        )

    async def _confirm_read_in_group(
        self,
        message_id: str,
        user_id: int,
        message_repo: MessageRepository,
        group_repo: GroupRepository,
    ):
        if message_id not in self.read_confirmations:
            # Для каждого сообщения создаем временное множество прочитавших
            # его адресатов
            self.read_confirmations[message_id] = set()
        self.read_confirmations[message_id].add(user_id)

        message = await message_repo.get_by_id(message_id)
        if not message:
            raise MessageNotFoundException(
                f"Сообщение {message_id} не найдено"
            )

        group = await group_repo.get_by_chat_id(message.chat_id)
        if not group:
            raise GroupNotFoundException(
                f"Группа для chat_id={message.chat_id} не найдена"
            )

        # Проверяем, все ли участники (кроме отправителя) прочитали
        participants_except_sender = set((user.id for user in group.participants)) - {
            message.sender_id
        }
        read_by = self.read_confirmations.get(message_id)
        if read_by is None:
            """
            Я тут столкнулся с некоторым race condition.
            Ситуация: все клиенты прочитали сообщение и прислали об этом
            уведомления.
            Логика в сокете универсальна: пришло подтверждение - вызови этот
            метод. Но что, если один клиент прислал отчет, запустил выполнение
            подтверждения о прочтении, и код дошел до 
            del self.read_confirmations[message_id],
            то есть все, нет в self.read_confirmations больше такого ключа -
            uuid сообщения, но в это же время другой клиент тоже прислал отчет
            о доставке, и этот метод тоже вызван и выполняется?
            Получается, что пока вызванный один раз метод уже все выполнил
            и удалил ключ из словаря, второй в этот момент еще выполняется
            и доходит до строки, где он проверяет по ключу, кто прочитал
            сообщение. Возникает KeyError, все падает.
            Поэтому мы просто аккуратно пытаемся получить из словаря множество
            прочитавших, и если оно на момент запроса уже None, то аккуратно
            выходим из функции.
            Важно, что мы здесь застрахованы от ошибки, что сообщение еще просто
            никто не прочитал: в самом начале выполнения метода, если ключа
            с uuid сообщения нет в словаре, этот ключ добавится со значением -
            пустым множеством.
            То есть, ситуация "гонки" возникла в тот момент, когда сообщение
            было во временном состоянии, когда код дублирующего метода начинал
            выполняться, но в процессе его выполнения словарь read_confirmations
            изменился, потеряв нужный ключ.
            Для чисто символического разделения логики
            мы определяем так:
            - если метод вернул True - обновить сообщению статус на "Прочитано";
            - если метод вернул False - не обновлять статус сообщения, еще
            не все прочитали сообщение;
            - если метод вернул None - тогда просто ничего не делай.
            Да, фактически два последних пункта - одно и то же по смыслу.
            Но есть отличия в семантике.
            """
            return None

        all_read = participants_except_sender == read_by

        if all_read:
            # Очищаем временное состояние
            del self.read_confirmations[message_id]
        return all_read
