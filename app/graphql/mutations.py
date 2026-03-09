import strawberry
from typing import Optional

from app.graphql.types import House, HouseError, Task, UserError, User
from .types import Task, User, UserError, CreateUserResult, AuthPayload, LoginResult, House, \
    HouseError
from ..models import Task as TaskModel
from ..models import TaskLife as TaskLifeModel
from ..models import House as HouseModel
from ..models import User as UserModel
from ..services.house_service import generate_unique_invite_code
from ..services.user_login import login_user
from strawberry.types import Info
from passlib.context import CryptContext


@strawberry.type
class TaskMutations:
    @strawberry.mutation
    def create_task(self,
                    info: Info,
                    title: str,
                    task_recurrence_id: int,
                    house_id: int,
                    description: Optional[str] = None,
                    weight: Optional[int] = None,
                    user_id: Optional[int] = None
                    ) -> Task:
        db = info.context["db"]

        task = TaskModel(title=title, description=description, weight=weight, house_id=house_id)
        db.add(task)
        db.commit()
        db.refresh(task)

        task_life = TaskLifeModel(task_id=task.id, recurrence_id=task_recurrence_id)
        db.add(task_life)
        db.commit()
        db.refresh(task_life)

        if user_id:
            user = db.get(UserModel, user_id)
            if user:  ##@todo need to check the user belong to this house
                task_life.assigned_users.append(user)
                db.commit()

        return Task(id=task.id, title=task.title, description=task.description, weight=task.weight)

    @strawberry.mutation
    def assign_task_to_user(self, info: Info, task_id: int, user_id: int) -> Task | UserError:
        db = info.context["db"]
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if task and user:
            task_life = db.query(TaskLifeModel).filter(TaskLifeModel.task_id == task_id).first()
            task_life.assigned_users.append(user)
            db.commit()
            db.refresh(task_life)
            return Task(id=task.id, title=task.title, description=task.description, weight=task.weight)
        else:
            return UserError(message="Task or user not found")

    @strawberry.mutation
    def remove_user_from_task(self, info: Info, task_id: int, user_id: int) -> Task | UserError:
        db = info.context["db"]
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if task and user:
            task_life = db.query(TaskLifeModel).filter(TaskLifeModel.task_id == task.id).first()
            task_life.assigned_users.remove(user)
            db.commit()
            db.refresh(task_life)
            return Task(id=task.id, title=task.title, description=task.description, weight=task.weight)
        else:
            return UserError(message="Task or user not found")


@strawberry.type
class UserMutations:
    @strawberry.mutation
    def create_user(self, info: Info, username: str, email: str, password: str) -> UserError | User:
        db = info.context["db"]

        email = email.lower()

        if db.query(UserModel).filter(UserModel.email == email).first():
            return UserError(message=f"An account with email '{email}' already exists.")

        pwd_context = CryptContext(schemes=["bcrypt"])
        hashed_password = pwd_context.hash(password)

        new_user = UserModel(name=username, email=email, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return User(
            id=new_user.id,
            email=new_user.email,
            name=new_user.name,
            is_active=new_user.is_active
        )

    @strawberry.mutation
    def login(self, info: Info, email: str, password: str) -> AuthPayload | UserError:
        db = info.context["db"]
        token = login_user(db, email, password)
        if token is None:
            return UserError(message="Invalid email or password.")
        return AuthPayload(token=token)


@strawberry.type
class HouseMutations:
    @strawberry.mutation
    def create_house(self, info: Info, name: str) -> HouseError | House:
        db = info.context["db"]
        if info.context.get("token_expired"):
            return HouseError(message="TOKEN_EXPIRED")
        user_id = info.context.get("user_id")
        if not user_id:
            return HouseError(message="User not authenticated.")

        invite_code = generate_unique_invite_code(db)

        new_house = HouseModel(name=name, invite_code=invite_code)
        db.add(new_house)
        db.commit()
        db.refresh(new_house)

        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return HouseError(message="User not found.")

        new_house.users.append(user)
        db.commit()
        db.refresh(new_house)

        return House(
            id=new_house.id,
            name=new_house.name,
            invite_code=new_house.invite_code
        )

    @strawberry.mutation
    def join_house_by_invitation_code(self, info: Info, invite_code: str) -> HouseError | House:
        db = info.context["db"]
        if info.context.get("token_expired"):
            return HouseError(message="TOKEN_EXPIRED")
        user_id = info.context.get("user_id")
        if not user_id:
            return HouseError(message="User not authenticated.")
        house = db.query(HouseModel).filter(HouseModel.invite_code == invite_code).first()
        if not house:
            return HouseError(message="House not found")
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return HouseError(message="User not found")
        house.users.append(user)
        db.commit()
        db.refresh(house)
        return House(
            id=house.id,
            name=house.name,
            invite_code=house.invite_code
        )

    @strawberry.mutation
    def add_user_to_house(self, info: Info, user_id: int, house_id: int) -> House:
        db = info.context["db"]
        house = db.query(HouseModel).filter(HouseModel.id == house_id).first()
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if house and user:
            house.users.append(user)
            db.commit()
            db.refresh(house)
        else:
            raise ValueError("House or user not found")

        return House(
            id=house.id,
            name=house.name,
            invite_code=house.invite_code
        )
