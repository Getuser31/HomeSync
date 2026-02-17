import strawberry
from typing import Optional
from .types import Task
from ..database import SessionLocal
from ..models import Task as TaskModel


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