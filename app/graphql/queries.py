import strawberry
from typing import List

from .types import Task, User, House
from ..models import Task as TaskModel
from ..models import User as UserModel
from ..models import House as HouseModel
from strawberry.types import Info


@strawberry.type
class TaskQueries:
    @strawberry.field
    def get_tasks(self, info: Info) -> List[Task]:
        db = info.context["db"]
        tasks = db.query(TaskModel).all()
        return [
            Task(
                id=t.id,
                title=t.title,
                description=t.description,
                is_completed=t.is_completed,
                house=House(
                    id=t.house.id,
                    name=t.house.name,
                    invite_code=t.house.invite_code
                ) if t.house else None
            )
            for t in tasks
        ]

    @strawberry.field
    def get_task_by_id(self, info: Info, id: int) -> Task | None:
        db = info.context["db"]
        t = db.query(TaskModel).filter(TaskModel.id == id).first()
        if t:
            return Task(
                id=t.id,
                title=t.title,
                description=t.description,
                is_completed=t.is_completed,
                house=House(
                    id=t.house.id,
                    name=t.house.name,
                    invite_code=t.house.invite_code
                ) if t.house else None
            )
        return None


@strawberry.type
class UserQueries:
    @strawberry.field
    def get_all_users(self, info: Info) -> List[User]:
        db = info.context["db"]
        users = db.query(UserModel).all()
        return [
            User(
                id=u.id,
                name=u.name,
                email=u.email,
                is_active=u.is_active,
                houses=[
                    House(id=h.id, name=h.name, invite_code=h.invite_code)
                    for h in u.houses
                ]
            )
            for u in users
        ]


@strawberry.type
class HouseQueries:
    @strawberry.field
    def get_house_by_invite_code(self, info: Info, invite_code: str) -> House | None:
        db = info.context["db"]
        house = db.query(HouseModel).filter(HouseModel.invite_code == invite_code).first()
        if house:
            return House(
                id=house.id,
                name=house.name,
                invite_code=house.invite_code
            )
        return None
