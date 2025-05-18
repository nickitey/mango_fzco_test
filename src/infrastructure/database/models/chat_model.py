from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities import ChatCategory
from src.infrastructure.database.models.base import Base


class ChatModel(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[ChatCategory] = mapped_column(
        Enum(ChatCategory), nullable=False
    )
    participants: Mapped[list["UserModel"]] = relationship(
        secondary="chats_users", back_populates="chats"
    )
