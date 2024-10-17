from pydantic import BaseModel
from datetime import datetime

class CommentCreate(BaseModel):
    zone_id: int
    user_id: int
    rating: int
    comment: str

class CommentViewResponse(BaseModel):
    id: int
    zone_id: int
    first_name: str
    last_name: str
    comment: str
    rating: int
    date_added: datetime
    update_date: datetime

    class Config:
        from_attributes = True

class CommentZoneInfo(BaseModel):
    id: int
    fullname: str
    comment: str
    date_comment: datetime
    rating: int

class CommentUpdate(BaseModel):
    comment: str


class DeleteComment(BaseModel):
    message: str
    is_deleted: bool