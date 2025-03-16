import nats
from nats.aio.client import Client as NATSClient
from typing import Optional
from pydantic import ValidationError

import entities
import dto
import exceptions
import codes

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

    async def create_user(self, user: entities.UserCreate) -> entities.UserResponse:
        try:
            msg = dto.CreateUserMessage(
                login=user.login,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                password=user.password
            )
            response = await self.nc.request("create_user", msg.model_dump_json().encode())
            res = dto.CreateUserResponse.model_validate_json(response.data)
            return entities.UserResponse(
                id=res.id,
                first_name=res.first_name,
                last_name=res.last_name,
                login=res.login,
                email=res.email,
                is_admin=res.is_admin,
                created_at=res.created_at
            )
        except ValidationError:
            err = dto.ErrorResponse.model_validate_json(response.data)
            if err.code == codes.USER_ALREADY_EXISTS:
                raise exceptions.UserAlreadyExistsException(login=user.login, email=user.email)
            if err.code == codes.INTERNAL_ERROR:
                raise exceptions.InternalException()

    async def get_user_by_id(self, user_id: int, actor_id: int) -> entities.UserResponse:
        try:
            msg = dto.GetUserByIdMessage(user_id=user_id, actor_id=actor_id)
            response = await self.nc.request("get_user_by_id", msg.model_dump_json().encode())
            res = dto.GetUserByIdResponse.model_validate_json(response.data)
            return entities.UserResponse(
                id=res.id,
                first_name=res.first_name,
                last_name=res.last_name,    
                login=res.login,
                email=res.email,
                is_admin=res.is_admin,
                created_at=res.created_at
            )
        except ValidationError:
            err = dto.ErrorResponse.model_validate_json(response.data)
            if err.code == codes.USER_NOT_FOUND:
                raise exceptions.UserNotFoundException(user_id=user_id)
            if err.code == codes.INTERNAL_ERROR:
                raise exceptions.InternalException()
    
    async def get_users(self, 
                        actor_id: int,
                        login: str, 
                        first_name: str, 
                        last_name: str,
                        limit: int = 100,
                        offset: int = 0,
                        ) -> list[entities.UserResponse]:
        try:
            msg = dto.GetUsersMessage(
                login=login,
                first_name=first_name,
                last_name=last_name,
                limit=limit,
                offset=offset,
                actor_id=actor_id
            )
            response = await self.nc.request("get_users", msg.model_dump_json().encode())
            return [entities.UserResponse(
                id=res.id,
                first_name=res.first_name,
                last_name=res.last_name,
                login=res.login,
                email=res.email,
                is_admin=res.is_admin,
                created_at=res.created_at
            ) for res in dto.GetUsersResponse.model_validate_json(response.data).Users]
        except ValidationError:
            err = dto.ErrorResponse.model_validate_json(response.data)
            if err.code == codes.INTERNAL_ERROR:
                raise exceptions.InternalException()
    
    async def login(self, items: entities.LoginItems) -> int:
        try:
            msg = dto.LoginMessage(login=items.login, password=items.password)
            response = await self.nc.request("login", msg.model_dump_json().encode())
            res = dto.LoginResponse.model_validate_json(response.data)
            return res.id
        except ValidationError:
            err = dto.ErrorResponse.model_validate_json(response.data)
            if err.code == codes.LOGIN_UNABLE:
                raise exceptions.LoginUnableException()
            if err.code == codes.INTERNAL_ERROR:
                raise exceptions.InternalException()
