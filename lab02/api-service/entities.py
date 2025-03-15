from pydantic import BaseModel

class UserCreate(BaseModel):
    nickname: str
    email: str

class UserResponse(BaseModel):
    id: int
    nickname: str
    email: str
