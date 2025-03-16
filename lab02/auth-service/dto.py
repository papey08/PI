from pydantic import BaseModel

class CreateTokensMessage(BaseModel):
    user_id: int

class CreateTokensResponse(BaseModel):
    access: str
    refresh: str

class RefreshTokensMessage(BaseModel):
    refresh: str

class RefreshTokensResponse(BaseModel):
    access: str
    refresh: str

class ErrorResponse(BaseModel):
    code: str
    details: str
