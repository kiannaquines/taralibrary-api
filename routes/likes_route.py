from fastapi import APIRouter, Depends, HTTPException, status
from schema.like_schema import LikeCreate, UnlikeResponse
from sqlalchemy.orm import Session
from services.db_services import get_db
from services.auth_services import get_current_user
from services.like_services import add_like, unlike_like
from database.database import User, Zones
from sqlalchemy.exc import SQLAlchemyError

likes_router = APIRouter()


@likes_router.post("/like/", response_model=LikeCreate)
async def like_zone(like_data: LikeCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    if current_user.id != like_data.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid user ID")
    
    zone_check = db.query(Zones).filter(Zones.id == like_data.zone_id).first()
    user_check = db.query(User).filter(User.id == like_data.user_id).first()

    if not zone_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")

    if not user_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        return add_like(db, like_data=like_data)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to add like: {str(e)}")
    
@likes_router.delete("/unlike/{like_id}", response_model=UnlikeResponse)
async def delete_like(like_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):   
    return unlike_like(db, like_id=like_id)

