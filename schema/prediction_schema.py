from pydantic import BaseModel, PositiveFloat
from datetime import datetime

class PredictionResponse(BaseModel):
    id: int
    zone_id: int
    estimated_count: int
    score: PositiveFloat
    first_seen: datetime
    last_seen: datetime
    scanned_minutes: int

    class Config:
        from_attributes = True