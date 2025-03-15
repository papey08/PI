from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import uvicorn

from user_accessor import UserAccessor
from entities import UserCreate, UserResponse

class HttpServer:
    def __init__(self, user_nats_url: str):
        self.user_accessor = UserAccessor(user_nats_url)
        self.app = FastAPI(lifespan=self.lifespan)

        self.app.post("/users", response_model=UserResponse)(self.create_user)
        self.app.get("/users/{user_id}", response_model=UserResponse)(self.get_user)

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        await self.user_accessor.__aenter__()
        yield
        await self.user_accessor.__aexit__(None, None, None)

    async def create_user(self, user: UserCreate):
        try:
            user = await self.user_accessor.create_user(user)
            return user
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_user(self, user_id: int):
        try:
            user = await self.user_accessor.get_user(user_id)
            if user == None:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    def run(self, host: str, port: int):
        uvicorn.run(self.app, host=host, port=port)