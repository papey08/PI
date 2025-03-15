from pydantic import BaseModel

class User(BaseModel):
    id: int
    nickname: str
    email: str
