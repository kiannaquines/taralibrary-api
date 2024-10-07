from pydantic import BaseModel

class ProfileCreate(BaseModel):
    user_id: int
    year: str
    college: str
    course: str

class UpdateProfile(BaseModel):
    user_id: int
    year: str
    college: str
    course: str

class DeleteProfile(BaseModel):
    message: str
    is_deleted: bool