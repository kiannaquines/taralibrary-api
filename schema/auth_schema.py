from pydantic import BaseModel

class RegisterSuccess(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str

class RegisterResponse(BaseModel):
    message: str
    user: RegisterSuccess

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str