from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from schema.profile_schema import ProfileCreate, UpdateProfile, DeleteProfile
from database.database import Profile, User
from fastapi import HTTPException, status
from services.auth_services import verify_current_user


def create_profile(
    db: Session,
    profile_create: ProfileCreate,
    current_user: User,
) -> ProfileCreate:

    if not verify_current_user(
        current_user_id=current_user.id,
        profile_creation_user_id=profile_create.user_id,
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to create a profile.",
        )

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
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists for this user.",
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


def get_profiles(db: Session, skip: int = 0, limit: int = 10) -> List[Profile]:
    return db.query(Profile).offset(skip).limit(limit).all()


def get_profile(db: Session, current_user: User, profile_id: int) -> Optional[Profile]:
    db_profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not verify_current_user(
        current_user_id=current_user.id,
        profile_creation_user_id=db_profile.user_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view profile.",
        )

    try:

        return db_profile
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


def update_profile(
    db: Session,
    profile_id: int,
    profile: UpdateProfile,
    current_user: User,
) -> UpdateProfile:

    db_profile = db.query(Profile).filter(Profile.id == profile_id).first()

    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    if not verify_current_user(
        current_user_id=current_user.id,
        profile_creation_user_id=profile.user_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update profile.",
        )

    if db_profile:
        for key, value in profile.dict(exclude_unset=True).items():
            setattr(db_profile, key, value)
        try:
            db.commit()
            db.refresh(db_profile)

            return UpdateProfile(
                user_id=db_profile.user_id,
                year=db_profile.year,
                college=db_profile.college,
                course=db_profile.course,
            )

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong while updating to the database.",
            )

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong.",
            )


def delete_profile(db: Session, current_user: User, profile_id: int) -> DeleteProfile:
    db_profile = db.query(Profile).filter(Profile.id == profile_id).first()

    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    if not verify_current_user(
        current_user_id=current_user.id,
        profile_creation_user_id=db_profile.user_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete profile.",
        )

    try:
        db.delete(db_profile)
        db.commit()
        return DeleteProfile(
            message="You have successfully removed profile",
            is_deleted=True,
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete profile",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )
