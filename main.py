from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from app.graphql.schema import schema
app = FastAPI()

# Create the GraphQL Router
graphql_app = GraphQLRouter(schema)

# Add the router to FastAPI (standard is "/graphql")
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
