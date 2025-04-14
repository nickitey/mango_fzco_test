from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    password: str
    hashed_password: str
