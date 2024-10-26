from sqlalchemy.orm import Session
from database.models import Comment, User, Zones
from schema.comment_schema import (
    CommentCreate,
    CommentViewResponse,
    CommentUpdate,
    CommentWithUserResponse,
    DeleteComment,
)
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from services.auth_services import verify_current_user


def add_comment(
    db: Session, current_user: User, comment_data: CommentCreate
) -> CommentCreate:

    if not verify_current_user(
        current_user_id=current_user.id,
        profile_creation_user_id=comment_data.user_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are not authorized to add a comment.",
        )

    zone_check = db.query(Zones).filter(Zones.id == comment_data.zone_id).first()

    if not zone_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found"
        )

    try:
        add_comment = Comment(
            user_id=comment_data.user_id,
            zone_id=comment_data.zone_id,
            rating=comment_data.rating,
            comment=comment_data.comment,
        )

        db.add(add_comment)
        db.commit()
        db.refresh(add_comment)
        return add_comment


    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add comment",
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )

def get_comments(db: Session) -> List[CommentWithUserResponse]:

    response = db.query(Comment).all()

    if not response:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No comments found",
        )

    try:

        return [
            CommentWithUserResponse(
                id=comment.id,
                full_name=f'{comment.user.first_name} {comment.user.last_name}',
                comment=comment.comment,
                rating=comment.rating,
                date_added=comment.date_added,
                update_date=comment.update_date,
            )
            for comment in response
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch comments: {str(e)}",
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch comments: {str(e)}",
        )


def get_comment(db: Session, comment_id: int) -> CommentViewResponse:

    response = db.query(Comment).filter(Comment.id == comment_id).first()

    if not response:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    try:

        return CommentViewResponse(
            id=response.id,
            zone_id=response.zone_id,
            user_id=response.user_id,
            comment=response.comment,
            date_added=response.date_added,
            update_date=response.update_date,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch comment: {str(e)}",
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch comment: ss{str(e)}",
        )


def edit_comment(
    db: Session,
    comment_id: int,
    update_data: CommentUpdate,
) -> CommentViewResponse:

    comment_db = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment_db:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    try:

        comment_db.comment = update_data.comment

        db.commit()
        db.refresh(comment_db)

        return CommentViewResponse(
            id=comment_db.id,
            zone_id=comment_db.zone_id,
            first_name=comment_db.user.first_name,
            last_name=comment_db.user.last_name,
            comment=comment_db.comment,
            rating=comment_db.rating,
            date_added=comment_db.date_added,
            update_date=comment_db.update_date,
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update comment: {str(e)}",
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update comment: {str(e)}",
        )


def delete_comment(db: Session, comment_id: int) -> DeleteComment:

    check_comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not check_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    try:
        db.query(Comment).filter(Comment.id == comment_id).delete(
            synchronize_session=False
        )
        db.commit()

        return DeleteComment(
            message="Comment deleted successfully",
            is_deleted=True,
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete comment: {str(e)}",
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete comment: {str(e)}",
        )
