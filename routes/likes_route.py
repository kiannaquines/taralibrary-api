from fastapi import APIRouter, Depends, HTTPException
from schema.like_schema import LikeCreate
from sqlalchemy.orm import Session
from services.db_services import get_db
from services.like_services import add_like
from database.database import User, Zones
from sqlalchemy.exc import SQLAlchemyError

likes_router = APIRouter()


@likes_router.post("/like/", response_model=LikeCreate)
async def like_zone(like_data: LikeCreate, db: Session = Depends(get_db)):
    zone_check = db.query(Zones).filter(Zones.id == like_data.zone_id).first()
    user_check = db.query(User).filter(User.id == like_data.user_id).first()

    if not zone_check:
        raise HTTPException(status_code=404, detail="Zone not found")

    if not user_check:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        return add_like(db, like_data=like_data)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Failed to add like: {str(e)}")

