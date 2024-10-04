from pydantic import BaseModel
from schema.user_schema import UserCreate


class RegisterResponse(BaseModel):
    message: str
    user: UserCreate

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str