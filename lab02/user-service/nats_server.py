import nats
import json
import asyncio

from memory_accessor import MemoryAccessor
import exceptions
import dto
import codes

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
        create_user = dto.CreateUserMessage.model_validate_json(msg.data)

        logging.info(f'creating user {create_user.email}')
        try:
            user = self.memory_accessor.create_user(
                create_user.login,
                create_user.first_name,
                create_user.last_name,
                create_user.email,
                create_user.password
            )
            logging.info(f'created user {create_user.email}')
            created_user = dto.CreateUserResponse(
                id=user.id,
                login=user.login,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                is_admin=user.is_admin,
                created_at=user.created_at
            )
            await msg.respond(created_user.model_dump_json().encode())
        except exceptions.UserAlreadyExistsException as e:
            logging.error(f'could not create user {create_user.email}: {e}')
            error = dto.ErrorResponse(
                code=codes.USER_ALREADY_EXISTS,
                details=str(e)
            )
            await msg.respond(error.model_dump_json().encode())
        except Exception as e:
            logging.error(f'could not create user: {e}')
            error = dto.ErrorResponse(
                code=codes.INTERNAL_ERROR,
                details=str(e)
            )
            await msg.respond(error.model_dump_json().encode())


    async def handle_get_by_id(self, msg):
        try:
            req = dto.GetUserByIdMessage.model_validate_json(msg.data)
            logging.info(f'getting user {req.user_id}')
            user = self.memory_accessor.get_user_by_id(req.user_id, req.actor_id)
            logging.info(f'got user {req.user_id}')
            await msg.respond(dto.GetUserByIdResponse(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                login=user.login,
                email=user.email,
                is_admin=user.is_admin,
                created_at=user.created_at
            ).model_dump_json().encode())
        except exceptions.UserNotFoundException as e:
            logging.error(f'could not get user {req.user_id}: {e}')
            error = dto.ErrorResponse(
                code=codes.USER_NOT_FOUND,
                details=str(e)
            )
            await msg.respond(error.model_dump_json().encode())
        except Exception as e:
            logging.error(f'could not get user: {e}')
            error = dto.ErrorResponse(
                code=codes.INTERNAL_ERROR,
                details=str(e)
            )
            await msg.respond(error.model_dump_json().encode())

    async def handle_get_users(self, msg):
        try:
            req = dto.GetUsersMessage.model_validate_json(msg.data)

            logging.info(f'getting users {req}')
            users = self.memory_accessor.get_users(
                login=req.login,
                first_name=req.first_name,
                last_name=req.last_name,
                limit=req.limit,
                offset=req.offset,
                actor_id=req.actor_id
            )
            logging.info(f'got users {filter}')
            await msg.respond(dto.GetUsersResponse(
                Users=[dto.GetUserByIdResponse(
                    id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    login=user.login,
                    email=user.email,
                    is_admin=user.is_admin,
                    created_at=user.created_at
                ) for user in users]
            ).model_dump_json().encode())
        except Exception as e:
            logging.error(f'could not get users {filter}: {e}')
            error = dto.ErrorResponse(
                code=codes.INTERNAL_ERROR,
                details=str(e)
            )
            await msg.respond(error.model_dump_json().encode())

    async def handle_login(self, msg):
        try:
            req = dto.LoginMessage.model_validate_json(msg.data)

            logging.info(f'logging in user {req.login}')
            user = self.memory_accessor.login(req.login, req.password)

            logging.info(f'logged in user {user.id}')
            await msg.respond(dto.LoginResponse(id=user.id).model_dump_json().encode())
        except exceptions.LoginUnableException as e:
            logging.error(f'could not login user {req.login}: {e}')
            error = dto.ErrorResponse(
                code=codes.LOGIN_UNABLE,
                details=str(e)
            )
            await msg.respond(error.model_dump_json().encode())
        except Exception as e:
            logging.error(f'could not login user: {e}')
            error = dto.ErrorResponse(
                code=codes.INTERNAL_ERROR,
                details=str(e)
            )
            await msg.respond(error.model_dump_json().encode())

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
