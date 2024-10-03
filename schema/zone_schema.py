from pydantic import BaseModel
from typing import List


class ZoneImageResponse(BaseModel):
    id: int
    image_url: str


class ZoneCreate(BaseModel):
    name: str
    description: str


class ZoneResponse(BaseModel):
    id: int
    name: str
    description: str
    images: List[ZoneImageResponse]
