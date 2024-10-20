from fastapi import APIRouter, Depends
from schema.device_schema import DeviceResponse
from services.device_services import get_all_devices
from services.db_services import get_db
from sqlalchemy.orm import Session
from typing import List
from database.models import User
from services.auth_services import get_current_user

device_router = APIRouter()


@device_router.get("/devices", response_model=List[DeviceResponse])
def get_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[DeviceResponse]:
    return get_all_devices(db=db)
