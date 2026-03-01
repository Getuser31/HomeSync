from fastapi import FastAPI, Depends
from strawberry.fastapi import GraphQLRouter

from app.graphql.schema import schema
from app.database import get_db

app = FastAPI()


async def get_context(db=Depends(get_db)):
    return {"db": db}


graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
