import nats
from nats.aio.client import Client as NATSClient
from typing import Optional
import json

from entities import UserCreate, UserResponse, LoginItems

class UserAccessor:
    def __init__(self, nats_url: str):
        self.nats_url = nats_url
        self.nc: Optional[NATSClient] = None

    async def __aenter__(self):
        self.nc = await nats.connect(self.nats_url)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.nc:
            await self.nc.close()

    async def create_user(self, user: UserCreate) -> UserResponse:
        response = await self.nc.request("create_user", user.model_dump_json().encode())
        return UserResponse.model_validate_json(response.data)

    async def get_user_by_id(self, user_id: int) -> UserResponse | None:
        response = await self.nc.request("get_user_by_id", str(user_id).encode())
        if not response.data:
            return None
        return UserResponse.model_validate_json(response.data)
    
    async def get_users(self, 
                        nickname: str = "", 
                        first_name: str = "", 
                        last_name: str = "",
                        limit: int = 100,
                        offset: int = 0) -> list[UserResponse] | None:
        response = await self.nc.request("get_users", json.dumps({
            "nickname": nickname,
            "first_name": first_name,
            "last_name": last_name,
            "limit": limit,
            "offset": offset
        }).encode())
        if not response.data:
            return None
        return [UserResponse.model_validate_json(user) for user in json.loads(response.data) if UserResponse.model_validate_json(user)]
    
    async def login(self, items: LoginItems) -> UserResponse | None:
        response = await self.nc.request("login", items.model_dump_json().encode())
        if not response.data:
            return None
        return UserResponse.model_validate_json(response.data)
