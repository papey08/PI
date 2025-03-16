from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import hashlib
import re
import jwt
from jwt.exceptions import ExpiredSignatureError

from auth_accessor import AuthAccessor
from user_accessor import UserAccessor
import entities
import exceptions

class HttpServer:
    PAGINATION_LIMIT = 100

    def __init__(self, auth_nats_url: str, user_nats_url: str, password_salt: str, jwt_secret: str):
        self.auth_accessor = AuthAccessor(auth_nats_url)
        self.user_accessor = UserAccessor(user_nats_url)
        
        self.password_salt = password_salt
        self.jwt_secret = jwt_secret
        
        self.app = FastAPI(lifespan=self.lifespan)

        self.app.post("/api/v1/register/", response_model=entities.UserResponse)(self.create_user)
        self.app.get("/api/v1/users/{user_id}/", response_model=entities.UserResponse)(self.get_user)
        self.app.get("/api/v1/users/", response_model=list[entities.UserResponse])(self.get_users)

        self.app.post("/api/v1/login/", response_model=entities.Tokens)(self.login)
        self.app.post("/api/v1/refresh/", response_model=entities.Tokens)(self.refresh)

        self.app.middleware("http")(self.auth_middleware)

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        await self.auth_accessor.__aenter__()
        await self.user_accessor.__aenter__()
        yield
        await self.auth_accessor.__aexit__(None, None, None)
        await self.user_accessor.__aexit__(None, None, None)

    async def create_user(self, user: entities.UserCreate):
        try:
            self.__validate_user(user)
            user.password = self.__hash_password(user.password)
            user = await self.user_accessor.create_user(user)
            return user
        except exceptions.UserAlreadyExistsException as e:
            return JSONResponse(status_code=400, content={"detail": str(e)})
        except Exception as e:
            return JSONResponse(status_code=500, content={"detail": "Internal server error"})
        
    async def auth_middleware(self, request: Request, call_next):
        if not request.url.path.startswith("/api/v1/users"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if auth_header is None or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
            
        access_token = auth_header.split(" ")
        if len(access_token) != 2:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
        
        try:
            payload = jwt.decode(
                access_token[1],
                self.jwt_secret,
                algorithms=["HS256"]
            )
            user_id = payload.get("user_id")
            request.state.user_id = user_id
        except ExpiredSignatureError:
            return JSONResponse(status_code=401, content={"detail": "Expired token"})
        except Exception:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        return await call_next(request)

    async def get_user(self, request: Request, user_id: int):
        try:
            user = await self.user_accessor.get_user_by_id(user_id, request.state.user_id)
            return user
        except exceptions.UserNotFoundException as e:
            return JSONResponse(status_code=404, content={"detail": str(e)})
        except Exception as e:
            return JSONResponse(status_code=500, content={"detail": "Internal server error"})
        
    async def get_users(self, request: Request,
                        login: str = Query(''), 
                        first_name: str = Query(''), 
                        last_name: str = Query(''),
                        limit: int = Query(PAGINATION_LIMIT),
                        offset: int = Query(0)):
        try:
            users = await self.user_accessor.get_users(request.state.user_id, login, first_name, last_name, limit, offset)
            return users
        except Exception as e:
            return JSONResponse(status_code=500, content={"detail": "Internal server error"})
        
    async def login(self, items: entities.LoginItems):
        try:
            items.password = self.__hash_password(items.password)
            user_id = await self.user_accessor.login(items)
            tokens = await self.auth_accessor.create_tokens(user_id)
            return tokens
        except exceptions.LoginUnableException as e:
            return JSONResponse(status_code=401, content={"detail": str(e)})
        except Exception as e:
            return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    async def refresh(self, refresh: entities.RefreshToken):
        try:
            tokens = await self.auth_accessor.refresh_tokens(refresh.refresh)
            if tokens == None:
                return JSONResponse(status_code=401, content={"detail": "expired tokens"})
            return tokens
        except exceptions.ExpiredRefreshTokenException as e:
            return JSONResponse(status_code=401, content={"detail": str(e)})
        except RuntimeError as e:
            return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    def run(self, host: str, port: int):
        uvicorn.run(self.app, host=host, port=port)

    def __hash_password(self, password: str) -> str:
        password = self.password_salt + password
        sha256_hash = hashlib.sha256()
        sha256_hash.update(password.encode('utf-8'))
        return sha256_hash.hexdigest()
    
    def __validate_user(self, user: entities.UserCreate):
        if not self.__validate_email(user.email):
            return JSONResponse(status_code=400, content={"detail": "Invalid email"})
        if not self.__validate_login(user.login):
            return JSONResponse(status_code=400, content={"detail": "login max length is 100"})
        if not self.__validate_name(user.first_name):
            return JSONResponse(status_code=400, content={"detail": "first name max length is 50"})
        if not self.__validate_name(user.last_name):
            return JSONResponse(status_code=400, content={"detail": "last name max length is 50"})
        if not self.__validate_password(user.password):
            return JSONResponse(
                status_code=400, 
                content={"detail": "password length must be between 8 and 20 and only latin letters and digits are allowed"})

    def __validate_email(self, email: str) -> bool:
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))
    
    def __validate_login(self, login: str) -> bool:
        return len(login) <= 100
    
    def __validate_name(self, name: str) -> bool:
        return len(name) <= 50
    
    def __validate_password(self, password: str) -> bool:
        return bool(re.match(r'^[a-zA-Z0-9]{8,20}$', password))
