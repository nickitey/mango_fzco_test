from dataclasses import dataclass
from datetime import datetime


@dataclass
class MessageDTO:
    id: str
    chat_id: int
    sender_id: int
    text: str
    timestamp: datetime
    is_read: bool
