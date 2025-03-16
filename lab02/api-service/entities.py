from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    login: str
    first_name: str
    last_name: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    login: str
    email: str
    is_admin: bool
    created_at: datetime

class LoginItems(BaseModel):
    login: str
    password: str

class Tokens(BaseModel):
    access: str
    refresh: str

class RefreshToken(BaseModel):
    refresh: str
