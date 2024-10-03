from fastapi import APIRouter, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session
from services.db_services import get_db
from services.zone_services import (
    create_zone,
    get_zone,
    get_zones,
    update_zone,
    delete_zone,
)
from schemas import (
    ZoneResponse,
    ZoneCreate
)
from typing import List
from fastapi.exceptions import HTTPException

zone_router = APIRouter()


@zone_router.post("/zones/", response_model=ZoneResponse)
def add_zone(name: str = Form(...),
    description: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)):
    zone = ZoneCreate(name=name, description=description)
    return create_zone(db=db, zone=zone, files=files)


@zone_router.get("/zones/", response_model=List[ZoneCreate])
def view_zones(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_zones(db=db, skip=skip, limit=limit)

@zone_router.get("/zones/{zone_id}", response_model=ZoneCreate)
def view_zone_details(zone_id: int, db: Session = Depends(get_db)):
    db_zone = get_zone(db=db, zone_id=zone_id)
    if db_zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    return db_zone

@zone_router.put("/zones/{zone_id}", response_model=ZoneCreate)
def edit_zone(zone_id: int, zone: ZoneCreate, db: Session = Depends(get_db)):
    db_zone = update_zone(db=db, zone_id=zone_id, zone=zone)
    if db_zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    return db_zone

@zone_router.delete("/zones/{zone_id}", response_model=ZoneCreate)
def remove_zone(zone_id: int, db: Session = Depends(get_db)):
    db_zone = delete_zone(db=db, zone_id=zone_id)
    if db_zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")
    return db_zone
