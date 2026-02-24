import strawberry
from typing import Optional, List
from datetime import datetime

@strawberry.type
class Task:
    id: int
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    house: "House"

@strawberry.type
class User:
    id: int
    email: str
    is_active: bool = True
    houses: List["House"]


@strawberry.type
class House:
    id: int
    name: str
    invite_code: str
    users: List[User]
    tasks: List[Task]


@strawberry.type
class TaskCategory:
    id: int
    name: str


@strawberry.type
class Assignment:
    id: int
    task: Task
    user: User
    due_date: datetime
    is_completed: bool
