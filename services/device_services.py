from fastapi import HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from database.models import Device
from schema.device_schema import DeviceResponse
from sqlalchemy.exc import SQLAlchemyError

from fastapi import Query

def get_all_devices(db: Session, page: int = Query(1, ge=1), limit: int = Query(500, gt=0)) -> dict:
    offset = (page - 1) * limit
    total_devices = db.query(Device).count()
    devices = db.query(Device).offset(offset).limit(limit).all()

    if not devices:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No devices found")
    
    try:
        return {
            "total": total_devices,
            "page": page,
            "limit": limit,
            "devices": [
                DeviceResponse(
                    id=device.id,
                    device_addr=device.device_addr,
                    date_detected=device.date_detected,
                    is_randomized=device.is_randomized,
                    device_power=device.device_power,
                    frame_type=device.frame_type,
                    zone=device.zone,
                    processed=device.processed,
                )
                for device in devices
            ]
        }
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve devices: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve devices")

