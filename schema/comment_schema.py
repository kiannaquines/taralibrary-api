from pydantic import BaseModel
from datetime import datetime

class CommentCreate(BaseModel):
    zone_id: int
    user_id: int
    comment: str

class CommentViewResponse(BaseModel):
    id: int
    zone_id: int
    user_id: int
    comment: str
    date_added: datetime
    update_date: datetime

    class Config:
        from_attributes = True


class CommentUpdate(BaseModel):
    comment: str


class DeleteComment(BaseModel):
    message: str
    is_deleted: bool