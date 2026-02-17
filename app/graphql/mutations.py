import strawberry
from typing import Optional
from .types import Task

@strawberry.type
class TaskMutations:
    @strawberry.mutation
    def create_task(self, title: str, description: Optional[str] = None) -> Task:
        print(f"Creating task: {title}")
        # Simulating ID generation
        return Task(id=3, title=title, description=description)