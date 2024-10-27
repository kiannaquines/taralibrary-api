from typing import Optional
from pydantic import BaseModel, PositiveFloat
from datetime import datetime

class PredictionResponse(BaseModel):
    id: int
    zone_name: str
    estimated_count: int
    score: Optional[PositiveFloat] 
    first_seen: datetime
    last_seen: datetime
    scanned_minutes: int

    class Config:
        from_attributes = True