from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: int
    login: str
    first_name: str
    last_name: str
    email: str
    password: str
    is_admin: bool
    created_at: datetime
