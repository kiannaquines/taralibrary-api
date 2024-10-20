from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    confirm_password: str
    first_name: str
    last_name: str


class UserUpdate(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str

class UserInDB(UserCreate):
    hashed_password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    profile_img: Optional[str] = None

    class Config:
        from_attributes = True


class UsersListResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    is_superuser: bool
    is_verified: bool
    profile_img: Optional[str] = None
    register_date: datetime
    update_date: datetime

    class Config:
        from_attributes = True

class UserUpdateResponse(BaseModel):
    message: str

class UserDeleteResponse(BaseModel):
    message: str

class AddUserResponse(BaseModel):
    message: str