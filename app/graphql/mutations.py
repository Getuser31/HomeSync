import strawberry
from typing import Optional
from .types import Task, User
from ..database import SessionLocal
from ..models import Task as TaskModel
from ..models import User as UserModel


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
