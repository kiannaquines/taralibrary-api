from fastapi import HTTPException
from sqlalchemy.orm import Session
from schema.like_schema import LikeCreate
from sqlalchemy.exc import SQLAlchemyError
from database.database import Like
import logging

def add_like(db: Session, like_data: LikeCreate) -> LikeCreate:
    logging.debug("Adding like for zone_id: %s, user_id: %s", like_data.zone_id, like_data.user_id)
    
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
            status_code=500, detail=f"An error occurred while adding like: {str(e)}"
        )
