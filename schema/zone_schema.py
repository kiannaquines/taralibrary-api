from pydantic import BaseModel
from typing import List


class ZoneImageResponse(BaseModel):
    id: int
    image_url: str


class ZoneCreate(BaseModel):
    name: str
    description: str

class ZoneRemoved(BaseModel):
    message: str
    is_deleted: bool

class ZoneResponse(BaseModel):
    id: int
    name: str
    description: str
    images: List[ZoneImageResponse]
