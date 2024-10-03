from pydantic import BaseModel

class ProfileCreate(BaseModel):
    user_id: int
    year: str
    college: str
    course: str