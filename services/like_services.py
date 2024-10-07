from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from schema.like_schema import LikeCreate, UnlikeResponse
from sqlalchemy.exc import SQLAlchemyError
from database.database import Like, Zones, User
from sqlalchemy import or_


def add_like(db: Session, current_user: User, like_data: LikeCreate) -> LikeCreate:

    if current_user.id != like_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid user ID"
        )

    zone_check = db.query(Zones).filter(Zones.id == like_data.zone_id).first()
    user_check = db.query(User).filter(User.id == like_data.user_id).first()
    check_like = (
        db.query(Like)
        .filter(
            or_(
                Zones.id == like_data.zone_id,
                User.id == like_data.user_id,
            )
        )
        .first()
    )

    if check_like:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You already liked this section",
        )

    if not zone_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found"
        )

    if not user_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db_like = Like(zone_id=like_data.zone_id, user_id=like_data.user_id)

    try:
        db.add(db_like)
        db.commit()
        db.refresh(db_like)
        return LikeCreate(
            zone_id=db_like.zone_id,
            user_id=db_like.user_id,
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="An error occurred while adding like"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="An error occurred while adding like"
        )


def unlike_like(db: Session, like_id: int) -> UnlikeResponse:

    db_like = db.query(Like).filter(Like.id == like_id).first()

    if db_like is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Like not found"
        )

    try:
        db.delete(db_like)
        db.commit()

        return UnlikeResponse(
            unliked=True,
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="An error occurred while deleting like"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Something went wrong while deleting like"
        )
