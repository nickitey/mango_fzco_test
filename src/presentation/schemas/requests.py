from pydantic import BaseModel, EmailStr

from src.domain.entities import ChatCategory


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class ChatCreate(BaseModel):
    name: str
    category: ChatCategory
    participant_ids: list[int]


class GroupCreate(BaseModel):
    name: str
    creator_id: int
    participant_ids: list[int]
    chat_id: int
