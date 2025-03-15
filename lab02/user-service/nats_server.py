import nats
import json
import asyncio

from entities import User
from memory_accessor import MemoryAccessor

class NatsServer:
    def __init__(self, nats_url):
        self.nc = None
        self.nats_url = nats_url
        self.memory_accessor = MemoryAccessor()

    async def connect(self):
        self.nc = await nats.connect(self.nats_url)

    async def handle_create(self, msg):
        data = json.loads(msg.data)
        user = self.memory_accessor.create_user(data["nickname"], data["email"])
        await msg.respond(user.model_dump_json().encode())

    async def handle_read(self, msg):
        user_id = int(msg.data.decode())
        user = self.memory_accessor.get_user(user_id)
        if user:
            await msg.respond(user.model_dump_json().encode())
        else:
            await msg.respond(b"")

    async def run(self):
        await self.connect()
        await self.nc.subscribe("create", cb=self.handle_create)
        await self.nc.subscribe("read", cb=self.handle_read)

        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            pass
        finally:
            await self.nc.close()
