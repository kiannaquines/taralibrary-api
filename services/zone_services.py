import uuid
import os
import shutil
from sqlalchemy.orm import Session, joinedload
from typing import List
from schema.zone_schema import (
    ZoneCreate,
    ZoneResponse,
    ZoneImageResponse,
)
from database.database import Zones, ZoneImage
from sqlalchemy.exc import SQLAlchemyError
from fastapi import UploadFile
from config.settings import UPLOAD_DIRECTORY
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException


def create_zone(db: Session, zone: ZoneCreate, files: List[UploadFile]) -> ZoneResponse:
    db_zone = Zones(name=zone.name, description=zone.description)

    try:
        db.add(db_zone)
        db.commit()
        db.refresh(db_zone)

        image_responses = []
        for file in files:
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            file_location = os.path.join(UPLOAD_DIRECTORY, unique_filename)

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
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def get_zones(db: Session, skip: int = 0, limit: int = 10) -> List[ZoneResponse]:
    zones = (
        db.query(Zones)
        .options(joinedload(Zones.images))
        .offset(skip)
        .limit(limit)
        .all()
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

    if zone is None:
        return None

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
    db: Session, zone_id: int, zone: ZoneCreate, files: UploadFile
) -> ZoneResponse:
    db_zone = db.query(Zones).filter(Zones.id == zone_id).first()

    if db_zone:
        for key, value in zone.dict(exclude_unset=True).items():
            setattr(db_zone, key, value)

        try:
            db.commit()
            db.refresh(db_zone)

            image_responses = []
            for file in files:
                unique_filename = f"{uuid.uuid4()}_{file.filename}"
                file_location = os.path.join(UPLOAD_DIRECTORY, unique_filename)

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

    return None


def delete_zone(db: Session, zone_id: int) -> Zones | None:
    db_zone = db.query(Zones).filter(Zones.id == zone_id).first()
    if db_zone:
        try:
            db.delete(db_zone)
            db.commit()

            for image in db_zone.images:
                os.remove(image.image_url)
                db.delete(image)
                db.commit()

            return db_zone
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    return None
