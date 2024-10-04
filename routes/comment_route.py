from fastapi import HTTPException, Depends, status, APIRouter
from database.database import Comment, User, Zones
from services.db_services import get_db
from sqlalchemy.orm import Session
from services.auth_services import get_current_user
from schema.comment_schema import (
    CommentCreate,
    CommentViewResponse,
    CommentUpdate,
    DeleteComment,
)
from sqlalchemy.exc import SQLAlchemyError
from services.comment_services import (
    add_comment,
    get_comments,
    get_comment,
    edit_comment,
    delete_comment,
)
from typing import List

comment_router = APIRouter()


@comment_router.post("/comments/", response_model=CommentCreate)
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    zone_check = db.query(Zones).filter(Zones.id == comment_data.zone_id).first()

    if not zone_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found"
        )

    try:
        new_comment = Comment(
            comment=comment_data.comment,
            user_id=comment_data.user_id,
            zone_id=comment_data.zone_id,
        )
        return add_comment(
            db=db,
            comment_data=new_comment,
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add comment: {str(e)}",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add comment: {str(e)}",
        )


@comment_router.get("/comments/", response_model=List[CommentViewResponse])
def view_comments(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return get_comments(db=db)


@comment_router.get("/comments/{comment_id}", response_model=CommentViewResponse)
def view_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_comment(db=db, comment_id=comment_id)


@comment_router.put("/comments/{comment_id}", response_model=CommentViewResponse)
def update_comment(
    comment_id: int,
    update_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return edit_comment(db=db, comment_id=comment_id, update_data=update_data)


@comment_router.delete(
    "/comments/{comment_id}",
    response_model=DeleteComment,
)
def remove_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_comment(db=db, comment_id=comment_id)
