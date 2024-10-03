from sqlalchemy.orm import Session
from typing import List
from schemas import (
    ZoneCreate,
    Zone,
)
from sqlalchemy.exc import SQLAlchemyError

def create_zone(db: Session, zone: ZoneCreate) -> Zone:
    db_zone = Zone(**zone.dict())
    try:
        db.add(db_zone)
        db.commit()
        db.refresh(db_zone)
        return db_zone
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_zones(db: Session, skip: int = 0, limit: int = 10) -> List[Zone]:
    return db.query(Zone).offset(skip).limit(limit).all()


def get_zone(db: Session, zone_id: int) -> Zone | None:
    return db.query(Zone).filter(Zone.id == zone_id).first()


def update_zone(db: Session, zone_id: int, zone: ZoneCreate) -> Zone | None:
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


def delete_zone(db: Session, zone_id: int) -> Zone | None:
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