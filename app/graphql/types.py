import strawberry
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from dataclasses import field

if TYPE_CHECKING:
    from app.services.period_key_service import generate_period_key
else:
    from app.services.period_key_service import generate_period_key


@strawberry.type
class Task:
    id: int
    title: str
    description: Optional[str] = None
    weight: int
    house: Optional["House"] = None
    task_lives: List["TaskLife"] = field(default_factory=list)

    @strawberry.field
    def is_completed(self) -> bool:
        if not self.task_lives:
            return False

        return all(task_life.is_completed() for task_life in self.task_lives)


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

    @strawberry.field
    def is_completed(self) -> bool:
        if not self.recurrence:
            return False

        current_period_key = generate_period_key(self.recurrence.name)
        return any(completion.period_key == current_period_key for completion in self.completions)


@strawberry.type
class TaskCompletion:
    id: int
    task_life: Optional[TaskLife] = None
    user_who_completed_id: Optional[int] = None
    completed_at: datetime
    # period_key permet de dire : "C'est la complétion pour la semaine 12 de 2024"
    period_key: str


@strawberry.type
class Role:
    id: int
    name: str


@strawberry.type
class RoleHouseUser:
    id: int
    role: Optional[Role] = None
    house: Optional["House"] = None


@strawberry.type
class User:
    id: int
    email: str
    name: str
    is_active: bool = True
    houses: List["House"] = field(default_factory=list)
    role_house_users: List[RoleHouseUser] = field(default_factory=list)

@strawberry.type
class House:
    id: int
    name: str
    invite_code: str
    users: List[User] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    current_user_role: Optional[Role] = None


@strawberry.type
class UserError:
    message: str

CreateUserResult = strawberry.union("CreateUserResult", types=(User, UserError))


@strawberry.type
class AuthPayload:
    token: str
    user: Optional[User] = None

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
class UncompletedTaskSuccess:
    success: bool = True


UncompletedTaskResult = strawberry.union("UncompletedTaskResult", types=(UncompletedTaskSuccess, TaskError))



@strawberry.type
class HouseError:
    message: str


CreateHouseResult = strawberry.union("CreateHouseResult", types=(House, HouseError))



