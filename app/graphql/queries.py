import strawberry
from typing import List

from app.graphql.types import Task
from .types import Task
from ..database import SessionLocal
from ..models import Task as TaskModel

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
