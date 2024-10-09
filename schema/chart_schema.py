from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime


class EstimatedCount(BaseModel):
    zone_name: str
    count: int

class ChartData(BaseModel):
    zone_name: str
    count: int
    first_seen: datetime
    last_seen: datetime
    scanned_minutes: int   

class ChartDataResponse(BaseModel):
    count: int
    time: str

class PredictionScore(BaseModel):
    zone_name: str
    count: int
    score: Decimal