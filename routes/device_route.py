from fastapi import APIRouter, Depends, Query
from services.device_services import get_all_devices
from services.db_services import get_db
from sqlalchemy.orm import Session
from database.models import User
from services.auth_services import get_current_user

device_router = APIRouter()


@device_router.get("/devices", response_model=dict)
def get_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(500, gt=0)
) -> dict:
    return get_all_devices(db=db, page=page, limit=limit)
