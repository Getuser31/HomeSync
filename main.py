import json
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from strawberry.fastapi import GraphQLRouter

from app.graphql.schema import schema
from app.database import get_db
from app.auth import decode_access_token

# Operations that do not require authentication
PUBLIC_OPERATIONS = {"Login", "CreateUser"}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path != "/graphql" or request.method == "OPTIONS":
            return await call_next(request)

        # Try to authenticate via Bearer token
        user_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[len("Bearer "):]
            user_id, _ = decode_access_token(token)

        if user_id:
            return await call_next(request)

        # No valid token — check if the operation is public
        try:
            body = await request.body()
            data = json.loads(body)
            operation_name = data.get("operationName") or ""
            if operation_name in PUBLIC_OPERATIONS:
                # Replay the body so downstream handlers can read it
                async def receive():
                    return {"type": "http.request", "body": body}

                request._receive = receive
                return await call_next(request)
        except Exception:
            pass

        response = JSONResponse(
            status_code=401,
            content={"errors": [{"message": "Not authenticated", "extensions": {"code": "UNAUTHENTICATED"}}]},
        )
        origin = request.headers.get("origin", "")
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        return response


app.add_middleware(AuthMiddleware)


async def get_context(request: Request, db=Depends(get_db)):
    user_id = None
    token_expired = False
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):]
        user_id, token_expired = decode_access_token(token)
    return {"db": db, "user_id": user_id, "token_expired": token_expired}


graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
