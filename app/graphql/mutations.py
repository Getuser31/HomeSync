import strawberry
from typing import Optional

from .types import Task, User, TaskCategory, Assignment, House
from ..database import SessionLocal
from ..models import Task as TaskModel
from ..models import TaskCategory as TaskCategoryModel
from ..models import House as HouseModel
from ..models import User as UserModel
from ..services.house_service import _generate_invite_code


@strawberry.type
class TaskMutations:
    @strawberry.mutation
    def create_task(self, title: str, description: Optional[str] = None) -> Task:
        db = SessionLocal()
        try:
            task = TaskModel(title=title, description=description)
            db.add(task)
            db.commit()
            db.refresh(task)
            return Task(id=task.id, title=task.title, description=task.description, is_completed=task.is_completed)
        finally:
            db.close()

    @strawberry.mutation
    def create_task_category(self, name: str) -> TaskCategory:
        db = SessionLocal()
        try:
            taskCategory = TaskCategoryModel(name=name)
            db.add(taskCategory)
            db.commit()
            db.refresh(taskCategory)
            return TaskCategory(id=taskCategory.id, name=taskCategory.name)
        finally:
            db.close()



@strawberry.type
class UserMutations:
    @strawberry.mutation
    def create_user(self, email: str, hashed_password: str) -> User:
        db = SessionLocal()
        try:
            new_user = UserModel(email=email, hashed_password=hashed_password)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return User(
                id=new_user.id,
                email=new_user.email,
                is_active=new_user.is_active
            )
        finally:
            db.close()


@strawberry.type
class HouseMutations:
    @strawberry.mutation
    def create_house(self, name: str) -> House:
        db = SessionLocal()
        try:
            invite_code = _generate_invite_code()

            new_house = HouseModel(name=name, invite_code=invite_code)
            db.add(new_house)
            db.commit()
            db.refresh(new_house)

            return House(
                id=new_house.id,
                name=new_house.name,
                invite_code=new_house.invite_code
            )
        finally:
            db.close()
