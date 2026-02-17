import strawberry
from .queries import TaskQueries, UserQueries
from .mutations import TaskMutations, UserMutations

@strawberry.type
class Query(TaskQueries, UserQueries):
    pass

@strawberry.type
class Mutation(TaskMutations, UserMutations):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)