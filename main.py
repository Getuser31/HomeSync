from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.graphql.schema import schema
from app.database import get_db
from app.auth import decode_access_token

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_context(request: Request, db=Depends(get_db)):
    user_id = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):]
        user_id = decode_access_token(token)
    return {"db": db, "user_id": user_id}


graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
