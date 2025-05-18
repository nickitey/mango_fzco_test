from dataclasses import dataclass, field

from src.config import hash_password, verify_password


@dataclass
class User:
    name: str
    email: str
    password_hash: str
    id: int | None = field(default=None)

    @classmethod
    def create_with_password(
        cls, name: str, email: str, password: str
    ) -> "User":
        hashed = hash_password(password)
        return cls(name=name, email=email, password_hash=hashed)

    def verify_password(self, plain_password: str) -> bool:
        return verify_password(plain_password, self.password_hash)
