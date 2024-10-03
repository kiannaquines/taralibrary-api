from sqlalchemy.orm import Session
from typing import List
from schemas import (
    ZoneCreate,
)
from database import Zones, ZoneImage
from sqlalchemy.exc import SQLAlchemyError
from fastapi import UploadFile
import os
import shutil
from settings import UPLOAD_DIRECTORY
import uuid
from fastapi.exceptions import HTTPException

def create_zone(db: Session, zone: ZoneCreate, files: List[UploadFile]) -> dict:
    db_zone = Zones(
        name=zone.name,
        description=zone.description
    )

    try:
        db.add(db_zone)
        db.commit()
        db.refresh(db_zone)

        image_urls = []
        for file in files:
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            file_location = os.path.join(UPLOAD_DIRECTORY, unique_filename)

            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            zone_image = ZoneImage(image_url=file_location, zone_id=db_zone.id)
            db.add(zone_image)
            image_urls.append(file_location)

        db.commit()

        return {
            "id": db_zone.id,
            "name": db_zone.name,
            "description": db_zone.description,
            "image_urls": image_urls,
        }
    
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
def get_zones(db: Session, skip: int = 0, limit: int = 10) -> List[ZoneCreate]:
    return db.query(Zones).offset(skip).limit(limit).all()


def get_zone(db: Session, zone_id: int) -> ZoneCreate:
    return db.query(Zones).filter(Zones.id == zone_id).first()


def update_zone(db: Session, zone_id: int, zone: ZoneCreate) -> Zones | None:
    db_zone = get_zone(db, zone_id)
    if db_zone:
        for key, value in zone.dict().items():
            setattr(db_zone, key, value)
        try:
            db.commit()
            db.refresh(db_zone)
            return db_zone
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    return None


def delete_zone(db: Session, zone_id: int) -> Zones | None:
    db_zone = get_zone(db, zone_id)
    if db_zone:
        try:
            db.delete(db_zone)
            db.commit()
            return db_zone
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    return None