from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    chat_id: int
    sender_id: int
    text: str
    timestamp: datetime
    is_read: bool
    id: str | None = field(default=None)
