from os import name

import strawberry
from typing import List

from .types import Task, User, House, HouseError, UserError, TaskRecurrence, TaskLife, TaskCompletion, RoleHouseUser, \
    Role
from ..models import Task as TaskModel, RoleHouseUser as RoleHouseUserModel
from ..models import User as UserModel
from ..models import Role as RoleUserModel
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
    def get_me(self, info: Info) -> UserError | User:
        db = info.context["db"]
        if info.context.get("token_expired"):
            raise ValueError("TOKEN_EXPIRED")
        userId = info.context['user_id']
        user = db.query(UserModel).filter(UserModel.id == userId).first()
        if not user:
            return UserError(message="User not found")
        return User(
            id=user.id,
            name=user.name,
            email=user.email,
            role_house_users=[
                RoleHouseUser(
                    id=rhu.id,
                    role=Role(id=rhu.role.id, name=rhu.role.name),
                    house=House(id=rhu.house.id, name=rhu.house.name, invite_code=rhu.house.invite_code),
                )
                for rhu in user.role_house_users
            ]
        )

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
            .options(joinedload(UserModel.role_house_users).joinedload(RoleHouseUserModel.role))
            .filter(UserModel.id == user_id)
            .first()
        )
        if not user:
            return None

        # Build a lookup: house_id -> RoleHouseUser for the current user
        role_by_house = {rhu.house_id: rhu for rhu in user.role_house_users}

        return [
            House(
                id=h.id,
                name=h.name,
                invite_code=h.invite_code,
                users=[
                    User(id=u.id, name=u.name, email=u.email, is_active=u.is_active)
                    for u in h.users
                ],
                current_user_role=Role(id=rhu.role.id, name=rhu.role.name)
                if (rhu := role_by_house.get(h.id)) else None,
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
            .options(
                joinedload(HouseModel.users).joinedload(UserModel.role_house_users).joinedload(RoleHouseUserModel.role))
            .options(joinedload(HouseModel.tasks)
                     .joinedload(TaskModel.task_lives)
                     .joinedload(TaskLifeModel.recurrence))
            .options(joinedload(HouseModel.tasks)
                     .joinedload(TaskModel.task_lives)
                     .joinedload(TaskLifeModel.completions))
            .filter(HouseModel.id == id)
            .first()
        )

        # Build a lookup: house_id -> RoleHouseUser for the current user
        role_by_house = {rhu.house_id: rhu for rhu in user.role_house_users}

        return House(
            id=house.id,
            name=house.name,
            invite_code=house.invite_code,
            current_user_role=Role(id=rhu.role.id, name=rhu.role.name)
            if (rhu := role_by_house.get(house.id)) else None,
            users=[
                User(id=u.id,
                     name=u.name,
                     email=u.email,
                     is_active=u.is_active,
                     role_house_users=[
                         RoleHouseUser(id=rhu.id,
                                       role=Role(id=rhu.role.id, name=rhu.role.name),
                                       )
                         for rhu in u.role_house_users if rhu.house_id == house.id]
                     )
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
                                User(id=u.id,
                                     name=u.name,
                                     email=u.email,
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


@strawberry.type
class RoleQueries:
    @strawberry.field
    def get_roles(self, info: Info) -> List[Role]:
        db = info.context["db"]
        roles = db.query(RoleUserModel).all()
        return [
            Role(
                id=r.id,
                name=r.name
            )
            for r in roles
        ]
