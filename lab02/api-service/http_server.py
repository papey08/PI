from fastapi import FastAPI, HTTPException, Query
from contextlib import asynccontextmanager
import uvicorn
import hashlib
import re

from auth_accessor import AuthAccessor
from user_accessor import UserAccessor
from entities import UserCreate, UserResponse, LoginItems, Tokens, RefreshToken

class HttpServer:
    PAGINATION_LIMIT = 100

    def __init__(self, auth_nats_url: str, user_nats_url: str, password_salt: str):
        self.auth_accessor = AuthAccessor(auth_nats_url)
        self.user_accessor = UserAccessor(user_nats_url)
        self.password_salt = password_salt
        self.app = FastAPI(lifespan=self.lifespan)

        self.app.post("/users", response_model=UserResponse)(self.create_user)
        self.app.get("/users/{user_id}", response_model=UserResponse)(self.get_user)
        self.app.get("/users", response_model=list[UserResponse])(self.get_users)

        self.app.post("/login", response_model=Tokens)(self.login)
        self.app.post("/refresh", response_model=Tokens)(self.refresh)

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        await self.auth_accessor.__aenter__()
        await self.user_accessor.__aenter__()
        yield
        await self.auth_accessor.__aexit__(None, None, None)
        await self.user_accessor.__aexit__(None, None, None)

    async def create_user(self, user: UserCreate):
        try:
            self.__validate_user(user)
            user.password = self.__hash_password(user.password)
            user = await self.user_accessor.create_user(user)
            return user
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_user(self, user_id: int):
        try:
            user = await self.user_accessor.get_user_by_id(user_id)
            if user == None:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def get_users(self, 
                        nickname: str = Query(None), 
                        first_name: str = Query(None), 
                        last_name: str = Query(None),
                        limit: int = Query(PAGINATION_LIMIT),
                        offset: int = Query(0)):
        try:
            users = await self.user_accessor.get_users(nickname, first_name, last_name, limit, offset)
            return users
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def login(self, items: LoginItems):
        try:
            items.password = self.__hash_password(items.password)
            user = await self.user_accessor.login(items)
            if user == None:
                raise HTTPException(status_code=400, detail="unable to login")
            tokens = await self.auth_accessor.create_tokens(user.id)
            return tokens
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def refresh(self, refresh: RefreshToken):
        try:
            tokens = await self.auth_accessor.refresh_tokens(refresh.refresh)
            if tokens == None:
                raise HTTPException(status_code=401, detail="expired tokens")
            return tokens
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    def run(self, host: str, port: int):
        uvicorn.run(self.app, host=host, port=port)

    def __hash_password(self, password: str) -> str:
        password = self.password_salt + password
        sha256_hash = hashlib.sha256()
        sha256_hash.update(password.encode('utf-8'))
        return sha256_hash.hexdigest()
    
    def __validate_user(self, user: UserCreate):
        if not self.__validate_email(user.email):
            raise HTTPException(status_code=400, detail="Invalid email")
        if not self.__validate_nickname(user.nickname):
            raise HTTPException(status_code=400, detail="nickname max length is 100")
        if not self.__validate_name(user.first_name):
            raise HTTPException(status_code=400, detail="first name max length is 50")
        if not self.__validate_name(user.last_name):
            raise HTTPException(status_code=400, detail="last name max length is 50")
        if not self.__validate_password(user.password):
            raise HTTPException(
                status_code=400, 
                detail="password length must be between 8 and 20 and only latin letters and digits are allowed")

    def __validate_email(self, email: str) -> bool:
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))
    
    def __validate_nickname(self, nickname: str) -> bool:
        return len(nickname) <= 100
    
    def __validate_name(self, name: str) -> bool:
        return len(name) <= 50
    
    def __validate_password(self, password: str) -> bool:
        return bool(re.match(r'^[a-zA-Z0-9]{8,20}$', password))
    