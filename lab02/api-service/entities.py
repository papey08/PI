from pydantic import BaseModel

class UserCreate(BaseModel):
    nickname: str
    first_name: str
    last_name: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    nickname: str
    email: str

class LoginItems(BaseModel):
    email: str
    password: str

class Tokens(BaseModel):
    access: str
    refresh: str

class RefreshToken(BaseModel):
    refresh: str
