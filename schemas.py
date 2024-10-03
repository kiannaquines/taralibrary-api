from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Optional

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
    year: Optional[str] = None
    college: Optional[str] = None
    course: Optional[str] = None

class Profile(ProfileCreate):
    id: int

    class Config:
        from_attributes = True

class ZoneImageCreate(BaseModel):
    image_url: HttpUrl
    zone_id: int

class ZoneImage(ZoneImageCreate):
    id: int

    class Config:
        from_attributes = True

class ZoneCreate(BaseModel):
    name: str
    description: str
    images: Optional[List[ZoneImageCreate]] = None

class Zone(ZoneCreate):
    id: int
    zone_images: List[ZoneImage] = []

    class Config:
        from_attributes = True
