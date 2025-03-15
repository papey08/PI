import nats
from nats.aio.client import Client as NATSClient
from typing import Optional

from entities import UserCreate, UserResponse

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
        response_data = await self.nc.request("create", user.model_dump_json().encode())
        return UserResponse.model_validate_json(response_data.data)

    async def get_user(self, user_id: int) -> UserResponse | None:
        response_data = await self.nc.request("read", str(user_id).encode())
        if not response_data.data:
            return None
        return UserResponse.model_validate_json(response_data.data)
