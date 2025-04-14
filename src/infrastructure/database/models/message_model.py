from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.models.base import Base


class MessageModel(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id", ondelete="SET NULL")
    )

    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    text: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False)
