import strawberry
from typing import Optional

@strawberry.type
class Task:
    id: int
    title: str
    description: Optional[str] = None
    is_completed: bool = False