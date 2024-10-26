from pydantic import BaseModel
from datetime import datetime

class DeviceResponse(BaseModel):
    id: int
    device_addr: str
    date_detected: datetime
    is_randomized: bool
    device_power: int
    frame_type: str
    zone: int
    processed: bool

    class Config:
        from_attributes = True