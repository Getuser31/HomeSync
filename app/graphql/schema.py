import strawberry
from .queries import TaskQueries, UserQueries, HouseQueries, TaskRecurrenceQueries
from .mutations import TaskMutations, UserMutations, HouseMutations

@strawberry.type
class Query(TaskQueries, UserQueries, HouseQueries, TaskRecurrenceQueries):
    pass

@strawberry.type
class Mutation(TaskMutations, UserMutations, HouseMutations):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)