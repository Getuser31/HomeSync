import strawberry
from typing import Optional, List
from datetime import datetime
from dataclasses import field


@strawberry.type
class Task:
    id: int
    title: str
    description: Optional[str] = None
    weight: int
    house: Optional["House"] = None
    task_lives: List["TaskLife"] = field(default_factory=list)


@strawberry.type
class TaskRecurrence:
    id: int
    name: str
    frequency_days: int


@strawberry.type
class TaskLife:
    id: int
    task: Optional[Task] = None
    recurrence: Optional[TaskRecurrence] = None
    assigned_users: List["User"] = field(default_factory=list)
    completions: List["TaskCompletion"] = field(default_factory=list)


@strawberry.type
class TaskCompletion:
    id: int
    task_life: Optional[TaskLife] = None
    user_who_completed_id: int
    completed_at: datetime
    period_key: str

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
class UserError:
    message: str

CreateUserResult = strawberry.union("CreateUserResult", types=(User, UserError))


@strawberry.type
class AuthPayload:
    token: str

LoginResult = strawberry.union("LoginResult", types=(AuthPayload, UserError))


@strawberry.type
class TaskError:
    message: str


CreateTaskResult = strawberry.union("CreateTaskResult", types=(Task, TaskError))

@strawberry.type
class DeleteTaskSuccess:
    success: bool = True


DeleteTaskResult = strawberry.union("DeleteTaskResult", types=(DeleteTaskSuccess, TaskError))


@strawberry.type
class HouseError:
    message: str


CreateHouseResult = strawberry.union("CreateHouseResult", types=(House, HouseError))



