import nats
from nats.aio.client import Client as NATSClient
from typing import Optional

from entities import Tokens

class AuthAccessor:
    def __init__(self, nats_url: str):
        self.nats_url = nats_url
        self.nc: Optional[NATSClient] = None

    async def __aenter__(self):
        self.nc = await nats.connect(self.nats_url)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.nc:
            await self.nc.close()

    async def create_tokens(self, user_id: int) -> Tokens:
        response = await self.nc.request("create_tokens", str(user_id).encode())
        if not response.data:
            return None
        return Tokens.model_validate_json(response.data)
    
    async def refresh_tokens(self, refresh_token: str) -> Tokens:
        response = await self.nc.request("refresh_tokens", refresh_token.encode())
        if not response.data:
            return None
        return Tokens.model_validate_json(response.data)
