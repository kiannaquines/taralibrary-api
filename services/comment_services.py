from sqlalchemy.orm import Session
from database.database import Comment
from schema.comment_schema import (
    CommentCreate,
    CommentViewResponse,
    CommentUpdate,
    DeleteComment,
)
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status


def add_comment(db: Session, comment_data: CommentCreate) -> CommentCreate:

    try:
        add_comment = Comment(
            user_id=comment_data.user_id,
            zone_id=comment_data.zone_id,
            comment=comment_data.comment,
        )

        db.add(add_comment)
        db.commit()
        db.refresh(add_comment)
        return add_comment

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add comment: {str(e)}",
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add comment: {str(e)}",
        )


def get_comments(db: Session) -> List[CommentViewResponse]:

    response = db.query(Comment).all()

    if not response:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No comments found",
        )
    
    try:

        return [
            CommentViewResponse(
                id=comment.id,
                zone_id=comment.zone_id,
                user_id=comment.user_id,
                comment=comment.comment,
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

    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    
    try:

        comment.comment = update_data.comment

        db.commit()
        db.refresh(comment)

        return CommentViewResponse(
            id=comment.id,
            zone_id=comment.zone_id,
            user_id=comment.user_id,
            comment=comment.comment,
            date_added=comment.date_added,
            update_date=comment.update_date,
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
        db.query(Comment).filter(Comment.id == comment_id).delete(synchronize_session=False)
        db.commit()

        return DeleteComment(
            comment_id=comment_id,
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
