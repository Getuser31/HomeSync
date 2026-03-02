import strawberry
from typing import Optional, List
from datetime import datetime
from dataclasses import field

@strawberry.type
class Task:
    id: int
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    house: Optional["House"] = None

@strawberry.type
class User:
    id: int
    email: str
    name: str
    is_active: bool = True
    houses: List["House"] = field(default_factory=list)


@strawberry.type
class House:
    id: int
    name: str
    invite_code: str
    users: List[User] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)


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
