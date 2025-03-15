from pydantic import BaseModel

class User(BaseModel):
    id: int
    nickname: str
    first_name: str
    last_name: str
    email: str
    password: str
