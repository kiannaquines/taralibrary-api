from fastapi import APIRouter, Depends
from schema.like_schema import LikeCreate, UnlikeResponse
from sqlalchemy.orm import Session
from services.db_services import get_db
from services.auth_services import get_current_user
from services.like_services import add_like, unlike_like
from database.database import User

likes_router = APIRouter()


@likes_router.post("/like/", response_model=LikeCreate)
async def like_zone(like_data: LikeCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return add_like(db, current_user=current_user, like_data=like_data)
   
@likes_router.delete("/unlike/{like_id}", response_model=UnlikeResponse)
async def delete_like(like_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):   
    return unlike_like(db, like_id=like_id)

