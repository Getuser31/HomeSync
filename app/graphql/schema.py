import strawberry
from .queries import TaskQueries
from .mutations import TaskMutations

@strawberry.type
class Query(TaskQueries):
    pass

@strawberry.type
class Mutation(TaskMutations):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)