import strawberry
from typing import List
from .types import Task

@strawberry.type
class TaskQueries:
    @strawberry.field
    def get_tasks(self) -> List[Task]:
        ##Add DB Logic
        return [
            Task(id=1, title="Laundry", description="Wash and dry clothes"),
            Task(id=2, title="Cleaning", description="Vacuum the living room")
        ]

    @strawberry.field
    def get_task_by_id(self, id: int) -> Task:
        ##Add DB Logic
        return Task(id=id, title="Laundry", description="Wash and dry clothes")
