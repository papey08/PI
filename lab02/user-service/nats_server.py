import nats
import json
import asyncio

from memory_accessor import MemoryAccessor

import logging
logging.basicConfig(
    level=logging.INFO
)

class NatsServer:
    def __init__(self, nats_url):
        self.nc = None
        self.nats_url = nats_url
        self.memory_accessor = MemoryAccessor()

    async def connect(self):
        self.nc = await nats.connect(self.nats_url)

    async def handle_create(self, msg):
        data = json.loads(msg.data)

        logging.info(f'creating user {data["email"]}')
        user = self.memory_accessor.create_user(
            data["nickname"],
            data["first_name"],
            data["last_name"], 
            data["email"], 
            data["password"]
        )
        logging.info(f'created user {data["email"]}')
        await msg.respond(user.model_dump_json().encode())

    async def handle_get_by_id(self, msg):
        user_id = int(msg.data.decode())

        logging.info(f'getting user {user_id}')
        user = self.memory_accessor.get_user_by_id(user_id)
        if user:
            logging.info(f'got user {user_id}')
            await msg.respond(user.model_dump_json().encode())
        else:
            logging.error(f'could not find user {user_id}')
            await msg.respond(b"")

    async def handle_get_users(self, msg):
        filter = json.loads(msg.data.decode())

        logging.info(f'getting users {filter}')
        users = self.memory_accessor.get_users(**filter)
        logging.info(f'got users {filter}')
        await msg.respond(json.dumps([user.model_dump_json() for user in users]).encode())

    async def handle_login(self, msg):
        data = json.loads(msg.data)

        logging.info(f'logging in user {data["email"]}')
        user = self.memory_accessor.login(data["email"], data["password"])
        if user:
            logging.info(f'logged in user {data["email"]}')
            await msg.respond(user.model_dump_json().encode())
        else:
            logging.error(f'could not login user {data["email"]}')
            await msg.respond(b"")

    async def run(self):
        await self.connect()
        await self.nc.subscribe("create_user", cb=self.handle_create)
        await self.nc.subscribe("get_user_by_id", cb=self.handle_get_by_id)
        await self.nc.subscribe("login", cb=self.handle_login)
        await self.nc.subscribe("get_users", cb=self.handle_get_users)

        logging.info('started nats server')

        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            pass
        finally:
            await self.nc.close()
