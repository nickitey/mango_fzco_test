from dataclasses import dataclass, field


@dataclass
class User:
    name: str
    email: str
    password_hash: str
    id: int | None = field(default=None)
