from datetime import datetime
import secrets
import string


import strawberry
from typing import Optional

from app.graphql.types import HouseError, User, UserError, House
from .types import Task, TaskCompletion, User, UserError, AuthPayload, House, \
    HouseError, TaskError, DeleteTaskSuccess, UncompletedTaskSuccess, RoleHouseUser, Role
from ..models import Task as TaskModel
from ..models import TaskLife as TaskLifeModel
from ..models import TaskCompletion as TaskCompletionModel
from ..models import House as HouseModel
from ..models import Role as RoleModel
from ..models import RoleHouseUser as RoleHouseUserModel
from ..models import User as UserModel
from ..services.house_service import generate_unique_invite_code
from ..services.user_login import login_user
from strawberry.types import Info
from passlib.context import CryptContext
from ..services.period_key_service import generate_period_key


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
    def delete_task(self, info: Info, task_id: int) -> DeleteTaskSuccess | TaskError:
        db = info.context["db"]
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if task:
            db.delete(task)
            db.commit()
            return DeleteTaskSuccess()
        else:
            return TaskError(message="Task not found")

    @strawberry.mutation
    def assign_task_to_user(self, info: Info, task_id: int, user_id: int) -> Task | TaskError | UserError:
        db = info.context["db"]
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if task and user:
            task_life = db.query(TaskLifeModel).filter(TaskLifeModel.task_id == task_id).first()
            task_life.assigned_users.append(user)
            db.commit()
            db.refresh(task_life)
            return Task(id=task.id, title=task.title, description=task.description, weight=task.weight)
        elif not task:
            return TaskError(message="Task not found")
        else:
            return UserError(message="User not found")

    @strawberry.mutation
    def remove_user_from_task(self, info: Info, task_id: int, user_id: int) -> Task | TaskError | UserError:
        db = info.context["db"]
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if task and user:
            task_life = db.query(TaskLifeModel).filter(TaskLifeModel.task_id == task.id).first()
            task_life.assigned_users.remove(user)
            db.commit()
            db.refresh(task_life)
            return Task(id=task.id, title=task.title, description=task.description, weight=task.weight)
        elif not task:
            return TaskError(message="Task not found")
        else:
            return UserError(message="User not found")

    @strawberry.mutation
    def complete_task(self, info: Info, task_id: int) -> TaskCompletion | TaskError | UserError:
        db = info.context["db"]
        user_id = info.context.get("user_id")
        if not user_id:
            return UserError(message="User not authenticated.")
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return UserError(message="User not found.")
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task:
            return TaskError(message="Task not found.")

        task_life = db.query(TaskLifeModel).filter(TaskLifeModel.task_id == task_id).first()
        period = generate_period_key(task_life.recurrence.name)

        task_completion = TaskCompletionModel(
            completed_at=datetime.now(),
            period_key=period,
            user_who_completed_id=user_id,
            task_life_id=task_life.id
        )
        db.add(task_completion)
        db.commit()
        db.refresh(task_completion)
        return TaskCompletion(
            id=task_completion.id,
            user_who_completed_id=task_completion.user_who_completed_id,
            completed_at=task_completion.completed_at,
            period_key=task_completion.period_key
        )

    @strawberry.mutation
    def uncompleted_task(self, info: Info, task_id: int) -> UncompletedTaskSuccess | TaskError | UserError:
        db = info.context["db"]
        user_id = info.context.get("user_id")
        if not user_id:
            return UserError(message="User not authenticated.")
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return UserError(message="User not found.")
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task:
            return TaskError(message="Task not found.")

        task_life = db.query(TaskLifeModel).filter(TaskLifeModel.task_id == task_id).first()
        period = generate_period_key(task_life.recurrence.name)

        task_completion = db.query(TaskCompletionModel).filter(TaskCompletionModel.task_life_id == task_life.id).first()
        if not task_completion:
            return TaskError(message="Task not found.")
        db.delete(task_completion)
        db.commit()
        return UncompletedTaskSuccess()





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

    @strawberry.mutation
    def update_user_role(self, info: Info, house_id: int, role_id: int, user_id: int) -> UserError | HouseError | User:
        db = info.context["db"]
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return UserError(message="User not found.")
        house = db.query(HouseModel).filter(HouseModel.id == house_id).first()
        if not house:
            return HouseError(message="House not found.")
        role = db.query(RoleModel).filter(RoleModel.id == role_id).first()

        currentRole = db.query(RoleHouseUserModel).filter(RoleHouseUserModel.user_id == user_id,
                                                          RoleHouseUserModel.house_id == house_id).first()
        if not role:
            return UserError(message="Role not found.")

        if currentRole and currentRole.role_id == 1:  ## We have to check if the current user is not the last admin in the House
            admins = db.query(RoleHouseUserModel).filter(RoleHouseUserModel.house_id == house_id,
                                                         RoleHouseUserModel.role_id == 1).all()
            if len(admins) == 1:
                return UserError(message="Cannot remove last admin from house.")

        if currentRole:
            currentRole.role_id = role_id
            db.commit()
            db.refresh(currentRole)
        else:
            newRole = RoleHouseUserModel(user_id=user_id, house_id=house_id, role_id=role_id)
            db.add(newRole)
            db.commit()
            db.refresh(newRole)

        finaleUserRole = db.query(RoleHouseUserModel).filter(RoleHouseUserModel.user_id == user_id,
                                                             RoleHouseUserModel.house_id == house_id).first()

        return User(
            id=user.id,
            email=user.email,
            name=user.name,
            role_house_users=[
                RoleHouseUser(
                    id=finaleUserRole.id,
                    role=Role(id=role.id, name=role.name)
                )
            ]
        )

    @strawberry.mutation
    def create_dummy_user_for_house(self, info: Info, houseId: int, username: str) -> UserError | HouseError | User:
        db = info.context["db"]
        house = db.query(HouseModel).filter(HouseModel.id == houseId).first()
        if not house:
            return HouseError(message="House not found.")

        email = f"{username}@{house.name}.com".lower()
        if db.query(UserModel).filter(UserModel.email == email).first():
            return UserError(message="User with this email already exists.")

        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for _ in range(16))
        new_user = UserModel(name=username, email=email, hashed_password=password, is_active=False)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        house.users.append(new_user)
        db.commit()
        db.refresh(house)

        return User(
            id=new_user.id,
            email=new_user.email,
            name=new_user.name,
            is_active=new_user.is_active
        )

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

    @strawberry.mutation
    def remove_user_from_house(self, info: Info, user_id: int, house_id: int) -> HouseError | UserError | House:
        db = info.context["db"]
        house = db.query(HouseModel).filter(HouseModel.id == house_id).first()
        if not house:
            return HouseError(message="House not found")

        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return UserError(message="User not found")

        house.users.remove(user)
        db.commit()
        db.refresh(house)

        if not user.is_active:
            db.delete(user)
            db.commit()

        return House(
            id=house.id,
            name=house.name,
            invite_code=house.invite_code
        )
