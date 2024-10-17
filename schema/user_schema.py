from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    confirm_password: str
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
    profile_img: str

    class Config:
        from_attributes = True