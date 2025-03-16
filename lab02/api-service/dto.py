from pydantic import BaseModel
from datetime import datetime

class CreateUserMessage(BaseModel):
    login: str
    first_name: str
    last_name: str
    email: str
    password: str

class CreateUserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    login: str
    email: str
    is_admin: bool
    created_at: datetime

class GetUserByIdMessage(BaseModel):
    user_id: int
    actor_id: int

class GetUserByIdResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    login: str
    email: str
    is_admin: bool
    created_at: datetime

class GetUsersMessage(BaseModel):
    login: str
    first_name: str
    last_name: str
    limit: int
    offset: int
    actor_id: int

class GetUsersResponse(BaseModel):
    Users: list[GetUserByIdResponse]

class LoginMessage(BaseModel):
    login: str
    password: str

class LoginResponse(BaseModel):
    id: int

class CreateTokensMessage(BaseModel):
    user_id: int

class CreateTokensResponse(BaseModel):
    access: str
    refresh: str

class RefreshTokensMessage(BaseModel):
    refresh: str

class RefreshTokensResponse(BaseModel):
    access: str
    refresh: str

class ErrorResponse(BaseModel):
    code: str
    details: str
