from pydantic import BaseModel, EmailStr, model_validator

from src.domain.entities import ChatCategory
from src.domain.exceptions import TooMuchUsersForPrivateChatException


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class ChatCreate(BaseModel):
    name: str
    category: ChatCategory
    participant_ids: list[int]

    @model_validator(mode="after")
    def validate_participant_ids(self):
        """
        В приватном чате не может состоять больше двух пользователей.
        Эту валидацию можно реализовать на нескольких уровнях, наиболее
        логичные: уровень представлений, уровень моделей и уровень базы.

        Оптимальное решение - уровень базы. Там можно создать триггер,
        функции компилируются и выполняются быстро, а надежность высока.
        Можно реализовать валидацию на уровне ORM. Но тогда запрос с заранее
        неподходящими данными пройдет глубже в слои приложения, хотя это можно
        отловить заранее, плюс нет никакой защиты от сырых SQL-запросов.
        Валидация на уровне контроллеров тоже не защищает от сырых запросов,
        но хотя бы не заставляет работать программу там, где заранее известно,
        что можно не работать.
        Остаются сценарии, когда в уже существующий чат пытаются добавить
        третьего пользователя, и это на уровне представлений уже никак
        не поймать, но для тестового задания мы оговариваем это, а реализацию
        оставим в качестве перспективного плана развития.

        Поначалу была мысль о проверке, что в чате не может быть не только
        больше двух пользователей, но и меньше двух, но потом подумалось:
        а вдруг человек хочет хоть где-то побыть один? И не стал реализовывать
        такую проверку.
        """
        if self.category == ChatCategory.PRIVATE:
            if len(self.participant_ids) > 2:
                raise TooMuchUsersForPrivateChatException(
                    "В приватном чате может быть не более двух пользователей"
                )
        return self


class GroupCreate(BaseModel):
    name: str
    creator_id: int
    participant_ids: list[int]
    chat_id: int
