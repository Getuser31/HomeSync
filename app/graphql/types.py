import strawberry
from typing import Optional

@strawberry.type
class Task:
    id: int
    title: str
    description: Optional[str] = None
    is_completed: bool = False


@strawberry.type
class User:
    id: int
    email: str
    is_active: bool = True
