from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from schemas import (
    ZoneImageCreate,
    ZoneImage,
)
from typing import List

def create_zone_image(db: Session, zone_image: ZoneImageCreate) -> ZoneImage:
    db_zone_image = ZoneImage(**zone_image.dict())
    try:
        db.add(db_zone_image)
        db.commit()
        db.refresh(db_zone_image)
        return db_zone_image
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_zone_images(db: Session, zone_id: int) -> List[ZoneImage]:
    return db.query(ZoneImage).filter(ZoneImage.zone_id == zone_id).all()


def delete_zone_image(db: Session, zone_image_id: int) -> ZoneImage | None:
    db_zone_image = db.query(ZoneImage).filter(ZoneImage.id == zone_image_id).first()
    if db_zone_image:
        try:
            db.delete(db_zone_image)
            db.commit()
            return db_zone_image
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    return None
