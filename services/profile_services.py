from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from schema.profile_schema import ProfileCreate
from database.database import Profile


def create_profile(db: Session, profile_create: ProfileCreate) -> ProfileCreate:
    db_profile = Profile(
        user_id=profile_create.user_id,
        year=profile_create.year,
        college=profile_create.college,
        course=profile_create.course,
    )
    try:
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception("Failed to create profile")

def get_profiles(db: Session, skip: int = 0, limit: int = 10) -> List[Profile]:
    return db.query(Profile).offset(skip).limit(limit).all()

def get_profile(db: Session, profile_id: int) -> Optional[Profile]:
    return db.query(Profile).filter(Profile.id == profile_id).first()

def update_profile(
    db: Session, profile_id: int, profile: ProfileCreate
) -> Profile:
    db_profile = get_profile(db, profile_id)
    if db_profile:
        for key, value in profile.dict(exclude_unset=True).items():
            setattr(db_profile, key, value)
        try:
            db.commit()
            db.refresh(db_profile)
            return db_profile
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception("Failed to update profile: " + str(e))
    return None


def delete_profile(db: Session, profile_id: int) -> Optional[Profile]:
    db_profile = get_profile(db, profile_id)
    if db_profile:
        try:
            db.delete(db_profile)
            db.commit()
            return db_profile
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception("Failed to delete profile")
    return None
