from pydantic import BaseModel

class LikeCreate(BaseModel):
    zone_id: int
    user_id: int

class UnlikeResponse(BaseModel):
    unliked: bool
