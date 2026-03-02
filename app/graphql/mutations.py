import strawberry
from typing import Optional

from .types import Task, User, TaskCategory, Assignment, House
from ..models import Task as TaskModel
from ..models import TaskCategory as TaskCategoryModel
from ..models import House as HouseModel
from ..models import User as UserModel
from ..services.house_service import generate_unique_invite_code
from strawberry.types import Info


@strawberry.type
class TaskMutations:
    @strawberry.mutation
    def create_task(self, title: str, info: Info, description: Optional[str] = None) -> Task:
        db = info.context["db"]

        task = TaskModel(title=title, description=description)
        db.add(task)
        db.commit()
        db.refresh(task)
        return Task(id=task.id, title=task.title, description=task.description, is_completed=task.is_completed)


@strawberry.mutation
def create_task_category(self, info: Info, name: str) -> TaskCategory:
    db = info.context["db"]

    taskCategory = TaskCategoryModel(name=name)
    db.add(taskCategory)
    db.commit()
    db.refresh(taskCategory)
    return TaskCategory(id=taskCategory.id, name=taskCategory.name)


@strawberry.type
class UserMutations:
    @strawberry.mutation
    def create_user(self, info: Info, email: str, hashed_password: str) -> User:
        db = info.context["db"]

        new_user = UserModel(email=email, name=name, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return User(
            id=new_user.id,
            email=new_user.email,
            name=new_user.name,
            is_active=new_user.is_active
        )


@strawberry.type
class HouseMutations:
    @strawberry.mutation
    def create_house(self, info: Info, name: str) -> House:
        db = info.context["db"]

        invite_code = generate_unique_invite_code(db)

        new_house = HouseModel(name=name, invite_code=invite_code)
        db.add(new_house)
        db.commit()
        db.refresh(new_house)

        return House(
            id=new_house.id,
            name=new_house.name,
            invite_code=new_house.invite_code
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
