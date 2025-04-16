from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.models.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)

    chats: Mapped[list["ChatModel"]] = relationship(
        back_populates="participants", secondary="chats_users"
    )
    groups: Mapped[list["GroupModel"]] = relationship(
        back_populates="participants", secondary="groups_users"
    )
