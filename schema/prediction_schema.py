from pydantic import BaseModel
from datetime import datetime

class PredictionResponse(BaseModel):
    id: int
    zone_id: int
    estimated_count: int
    first_seen: datetime
    last_updated: datetime
    scanned_minutes: int

    class Config:
        from_attributes = True