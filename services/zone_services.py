import uuid
import os
import shutil
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from schema.zone_schema import ZoneCreate, ZoneResponse, ZoneImageResponse, ZoneRemoved
from database.database import Zones, ZoneImage
from sqlalchemy.exc import SQLAlchemyError
from fastapi import UploadFile, status
from config.settings import ZONE_UPLOAD_DIRECTORY
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException


def create_zone(
    db: Session,
    zone: ZoneCreate,
    files: List[UploadFile],
) -> ZoneResponse:
    db_zone = Zones(name=zone.name, description=zone.description)

    try:
        db.add(db_zone)
        db.commit()
        db.refresh(db_zone)

        image_responses = []
        for file in files:
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            file_location = os.path.join(ZONE_UPLOAD_DIRECTORY, unique_filename)

            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            zone_image = ZoneImage(image_url=file_location, zone_id=db_zone.id)
            db.add(zone_image)
            db.commit()

            image_responses.append(
                ZoneImageResponse(id=zone_image.id, image_url=zone_image.image_url)
            )

        return ZoneResponse(
            id=db_zone.id,
            name=db_zone.name,
            description=db_zone.description,
            images=image_responses,
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")

def get_zones(db: Session, skip: int = 0, limit: int = 10) -> List[ZoneResponse]:
    zones = (
        db.query(Zones)
        .options(joinedload(Zones.images))
        .offset(skip)
        .limit(limit)
        .all()
    )

    if not zones:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No zones found"
        )

    zone_responses = []
    for zone in zones:
        zone_responses.append(
            ZoneResponse(
                id=zone.id,
                name=zone.name,
                description=zone.description,
                images=[
                    ZoneImageResponse(id=image.id, image_url=image.image_url)
                    for image in zone.images
                ],
            )
        )

    return zone_responses

def get_zone(db: Session, zone_id: int) -> ZoneResponse:
    zone = (
        db.query(Zones)
        .filter(Zones.id == zone_id)
        .options(joinedload(Zones.images))
        .first()
    )

    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found"
        )

    return ZoneResponse(
        id=zone.id,
        name=zone.name,
        description=zone.description,
        images=[
            ZoneImageResponse(id=image.id, image_url=image.image_url)
            for image in zone.images
        ],
    )

def update_zone(
    db: Session,
    zone_id: int,
    zone: ZoneCreate,
    files: Optional[List[UploadFile]] = None,
) -> ZoneResponse:
    db_zone = db.query(Zones).filter(Zones.id == zone_id).first()

    if not db_zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found"
        )

    try:
        for key, value in zone.dict(exclude_unset=True).items():
            setattr(db_zone, key, value)

        db.commit()
        db.refresh(db_zone)

        if files:
            image_responses = []
            for file in files:
                unique_filename = f"{uuid.uuid4()}_{file.filename}"
                file_location = os.path.join(ZONE_UPLOAD_DIRECTORY, unique_filename)

                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

                zone_image = ZoneImage(image_url=file_location, zone_id=db_zone.id)
                db.add(zone_image)
                db.commit()

                image_responses.append(
                    ZoneImageResponse(id=zone_image.id, image_url=zone_image.image_url)
                )

        return ZoneResponse(
            id=db_zone.id,
            name=db_zone.name,
            description=db_zone.description,
            images=[
                ZoneImageResponse(id=image.id, image_url=image.image_url)
                for image in db_zone.images
            ],
        )
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")

def delete_zone(db: Session, zone_id: int) -> ZoneRemoved | None:
    db_zone = db.query(Zones).filter(Zones.id == zone_id).first()

    if not db_zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found",
        )

    try:
        db.delete(db_zone)
        db.commit()

        for image in db_zone.images:
            os.remove(image.image_url)
            db.delete(image)
            db.commit()

        return ZoneRemoved(
            message="You have successfully removed the zone",
            is_deleted=True,
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise e
