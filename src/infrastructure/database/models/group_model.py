from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base


class GroupModel(Base):
    __tablename__ = "groups"
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(nullable=False)
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    participants: Mapped[list["UserModel"]] = relationship(
        secondary="groups_users", back_populates="groups"
    )
