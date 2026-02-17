import strawberry
from typing import List

from app.graphql.types import Task
from .types import Task, User
from ..database import SessionLocal
from ..models import Task as TaskModel
from ..models import User as UserModel

@strawberry.type
class TaskQueries:
    @strawberry.field
    def get_tasks(self) -> List[Task]:
        db = SessionLocal()
        try:
            tasks = db.query(TaskModel).all()
            return [
                Task(
                    id=t.id, 
                    title=t.title, 
                    description=t.description, 
                    is_completed=t.is_completed
                ) for t in tasks
            ]
        finally:
            db.close()

    @strawberry.field
    def get_task_by_id(self, id: int) -> Task | None:
        db = SessionLocal()
        try:
            t = db.query(TaskModel).filter(TaskModel.id == id).first()
            if t:
                return Task(
                    id=t.id, 
                    title=t.title, 
                    description=t.description, 
                    is_completed=t.is_completed
                )
            return None
        finally:
            db.close()


@strawberry.type
class UserQueries:
    @strawberry.field
    def get_all_users(self) -> List[User]:
        db = SessionLocal()
        try:
            users = db.query(UserModel).all()
            return [
                User(
                    id=u.id,
                    email=u.email,
                    is_active=u.is_active
                ) for u in users
            ]
        finally:
            db.close()
