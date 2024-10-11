from pydantic import BaseModel
from typing import List
from schema.comment_schema import CommentViewResponse
from schema.chart_schema import ChartDataResponse

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


class ZoneInfoResponse(BaseModel):
    id: int
    name: str
    description: str
    comments: List[CommentViewResponse]
    images: List[ZoneImageResponse]
    predictions: List[ChartDataResponse]
    total_rating: float
    total_reviews: int

class PopularSectionResponse(BaseModel):
    section_id: int
    section_name: str
    total_rating: float
    image_url: str

class RecommendSectionResponse(BaseModel):
    section_id: int
    status: str
    section_name: str
    description: str
    total_rating: float
    image_url: str


class AllSectionResponse(BaseModel):
    section_id: int
    section_name: str
    description: str
    total_rating: float
    image_url: str

