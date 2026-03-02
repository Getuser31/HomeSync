import strawberry
from .queries import TaskQueries, UserQueries, HouseQueries
from .mutations import TaskMutations, UserMutations, HouseMutations

@strawberry.type
class Query(TaskQueries, UserQueries, HouseQueries):
    pass

@strawberry.type
class Mutation(TaskMutations, UserMutations, HouseMutations):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)