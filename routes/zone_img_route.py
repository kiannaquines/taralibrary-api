from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from services.db_services import (
    get_db
)
from services.zone_img_services import (
    create_zone_image,
    get_zone_images,
    delete_zone_image,
)
from schemas import (
    ZoneImage,
    ZoneImageCreate,
)
from typing import List


zone_img_router = APIRouter()

@zone_img_router.post("/zone-images/", response_model=ZoneImage)
def add_zone_image(zone_image: ZoneImageCreate, db: Session = Depends(get_db)):
    return create_zone_image(db=db, zone_image=zone_image)

@zone_img_router.get("/zone-images/{zone_id}", response_model=List[ZoneImage])
def view_zone_images(zone_id: int, db: Session = Depends(get_db)):
    return get_zone_images(db=db, zone_id=zone_id)

@zone_img_router.delete("/zone-images/{zone_image_id}", response_model=ZoneImage)
def remove_zone_image(zone_image_id: int, db: Session = Depends(get_db)):
    db_zone_image = delete_zone_image(db=db, zone_image_id=zone_image_id)
    if db_zone_image is None:
        raise HTTPException(status_code=404, detail="Zone Image not found")
    return db_zone_image
