from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from schemas import (
    Profile,
    ProfileCreate
)

def create_profile(db: Session, profile: ProfileCreate) -> Profile:
    db_profile = Profile(**profile.dict())
    try:
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_profiles(db: Session, skip: int = 0, limit: int = 10) -> List[Profile]:
    return db.query(Profile).offset(skip).limit(limit).all()


def get_profile(db: Session, profile_id: int) -> Profile | None:
    return db.query(Profile).filter(Profile.id == profile_id).first()


def update_profile(
    db: Session, profile_id: int, profile: ProfileCreate
) -> Profile | None:
    db_profile = get_profile(db, profile_id)
    if db_profile:
        for key, value in profile.dict().items():
            setattr(db_profile, key, value)
        try:
            db.commit()
            db.refresh(db_profile)
            return db_profile
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    return None


def delete_profile(db: Session, profile_id: int) -> Profile | None:
    db_profile = get_profile(db, profile_id)
    if db_profile:
        try:
            db.delete(db_profile)
            db.commit()
            return db_profile
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    return None