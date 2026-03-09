import strawberry
from typing import List

from app.graphql.types import House, HouseError, UserError
from .types import Task, User, House, HouseError, UserError, TaskRecurrence, TaskLife, TaskCompletion
from ..models import Task as TaskModel
from ..models import User as UserModel
from ..models import House as HouseModel
from ..models import TaskRecurrence as TaskRecurrenceModel
from ..models import TaskLife as TaskLifeModel
from strawberry.types import Info
from sqlalchemy.orm import joinedload


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
                weight=t.weight,
                house=House(
                    id=t.house.id,
                    name=t.house.name,
                    invite_code=t.house.invite_code
                ) if t.house else None,
                task_lives=[
                    TaskLife(
                        id=tl.id,
                        recurrence=TaskRecurrence(
                            id=tl.recurrence.id,
                            name=tl.recurrence.name,
                            frequency_days=tl.recurrence.frequency_days
                        ) if tl.recurrence else None,
                        completions=[
                            TaskCompletion(
                                id=tc.id,
                                completed_at=tc.completed_at,
                                period_key=tc.period_key,
                                user_who_completed_id=tc.user_who_completed_id
                            )
                            for tc in tl.completions
                        ],
                        assigned_users=[
                            User(
                                id=au.id,
                                name=au.name,
                                email=au.email,
                            )
                            for au in tl.assigned_users
                        ]
                    )
                    for tl in t.task_lives
                ]
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

    @strawberry.field
    def get_house_by_user(self, info: Info) -> List[House] | None:
        db = info.context["db"]
        if info.context.get("token_expired"):
            raise ValueError("TOKEN_EXPIRED")
        user_id = info.context.get("user_id")
        if not user_id:
            return None
        user = (
            db.query(UserModel)
            .options(joinedload(UserModel.houses).joinedload(HouseModel.users))
            .filter(UserModel.id == user_id)
            .first()
        )
        if not user:
            return None
        return [
            House(
                id=h.id,
                name=h.name,
                invite_code=h.invite_code,
                users=[
                    User(id=u.id, name=u.name, email=u.email, is_active=u.is_active)
                    for u in h.users
                ],
            )
            for h in user.houses
        ]

    @strawberry.field
    def get_house_by_id(self, info: Info, id: int) -> UserError | HouseError | House:
        db = info.context['db']
        house = db.query(HouseModel).filter(HouseModel.id == id).first()
        userId = info.context['user_id']
        if not userId:
            return UserError(message="User not authenticated.")

        user = db.query(UserModel).filter(UserModel.id == userId).first()
        if not user:
            return UserError(message="User not found.")

        if not house:
            return HouseError(message="House not found")

        house = (
            db.query(HouseModel)
            .options(joinedload(HouseModel.users))
            .options(joinedload(HouseModel.tasks)
                     .joinedload(TaskModel.task_lives)
                     .joinedload(TaskLifeModel.recurrence))
            .options(joinedload(HouseModel.tasks)
                     .joinedload(TaskModel.task_lives)
                     .joinedload(TaskLifeModel.completions))
            .filter(HouseModel.id == id)
            .first()
        )

        return House(
            id=house.id,
            name=house.name,
            invite_code=house.invite_code,
            users=[
                User(id=u.id, name=u.name, email=u.email, is_active=u.is_active)
                for u in house.users
            ],
            tasks=[
                Task(
                    id=t.id,
                    title=t.title,
                    description=t.description,
                    weight=t.weight,
                    task_lives=[
                        TaskLife(
                            id=tl.id,
                            recurrence=TaskRecurrence(
                                id=tl.recurrence.id,
                                name=tl.recurrence.name,
                                frequency_days=tl.recurrence.frequency_days,
                            ) if tl.recurrence else None,
                            completions=[
                                TaskCompletion(
                                    id=tc.id,
                                    user_who_completed_id=tc.user_who_completed_id,
                                    completed_at=tc.completed_at,
                                    period_key=tc.period_key,
                                ) for tc in tl.completions
                            ],
                            assigned_users=[
                                User(id=u.id, name=u.name, email=u.email,
                                     is_active=u.is_active)
                                for u in tl.assigned_users
                            ],
                        ) for tl in t.task_lives
                    ],
                ) for t in house.tasks
            ]
        )


@strawberry.type
class TaskRecurrenceQueries:
    @strawberry.field
    def get_task_recurrences(self, info: Info) -> List[TaskRecurrence]:
        db = info.context["db"]
        recurrences = db.query(TaskRecurrenceModel).all()
        return [
            TaskRecurrence(
                id=r.id,
                name=r.name,
                frequency_days=r.frequency_days
            )
            for r in recurrences
        ]
