from pydantic import BaseModel
from datetime import datetime


class ChartData(BaseModel):
    zone_name: str
    count: int
    first_seen: datetime
    last_seen: datetime
    scanned_minutes: int   