from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str

class UserInDB(UserCreate):
    hashed_password: str

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

class ProfileCreate(BaseModel):
    user_id: int
    year: Optional[str]
    college: Optional[str]
    course: Optional[str]


class ZoneCreate(BaseModel):
    name: str
    description: str

class ZoneResponse(BaseModel):
    id: int
    name: str
    description: str
    image_urls: List[str]
