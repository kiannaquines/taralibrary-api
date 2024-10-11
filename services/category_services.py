from sqlalchemy.orm import Session
from database.database import Category, User
from schema.category_schema import *
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status


def add_category(db: Session, category_data: CategoryCreate) -> CategoryResponse:
    try:
        add_category = Category(
            category=category_data.category_name,
        )

        db.add(add_category)
        db.commit()
        db.refresh(add_category)

        return CategoryResponse(
            category_id=add_category.id,
            category_name=add_category.category,
            date_added=add_category.date_added,
            update_date=add_category.update_date,
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add category",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


def get_categories(db: Session) -> List[CategoryResponse]:

    response = db.query(Category).all()

    if not response:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No category found",
        )

    try:

        return [
            CategoryResponse(
                category_id=category.id,
                category_name=category.category,
                date_added=category.date_added,
                update_date=category.update_date,
            )
            for category in response
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch category: {str(e)}",
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Something went wrong: {str(e)}",
        )


# def get_comment(db: Session, comment_id: int) -> CommentViewResponse:

#     response = db.query(Comment).filter(Comment.id == comment_id).first()

#     if not response:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Comment not found",
#         )

#     try:

#         return CommentViewResponse(
#             id=response.id,
#             zone_id=response.zone_id,
#             user_id=response.user_id,
#             comment=response.comment,
#             date_added=response.date_added,
#             update_date=response.update_date,
#         )

#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to fetch comment: {str(e)}",
#         )

#     except SQLAlchemyError as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to fetch comment: ss{str(e)}",
#         )


# def edit_comment(
#     db: Session,
#     comment_id: int,
#     update_data: CommentUpdate,
# ) -> CommentViewResponse:

#     comment_db = db.query(Comment).filter(Comment.id == comment_id).first()

#     if not comment_db:

#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Comment not found",
#         )

#     try:

#         comment_db.comment = update_data.comment

#         db.commit()
#         db.refresh(comment_db)

#         return CommentViewResponse(
#             id=comment_db.id,
#             zone_id=comment_db.zone_id,
#             user_id=comment_db.user_id,
#             comment=comment_db.comment,
#             date_added=comment_db.date_added,
#             update_date=comment_db.update_date,
#         )

#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to update comment: {str(e)}",
#         )

#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to update comment: {str(e)}",
#         )


# def delete_comment(db: Session, comment_id: int) -> DeleteComment:

#     check_comment = db.query(Comment).filter(Comment.id == comment_id).first()

#     if not check_comment:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Comment not found",
#         )

#     try:
#         db.query(Comment).filter(Comment.id == comment_id).delete(
#             synchronize_session=False
#         )
#         db.commit()

#         return DeleteComment(
#             message="Comment deleted successfully",
#             is_deleted=True,
#         )

#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to delete comment: {str(e)}",
#         )

#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to delete comment: {str(e)}",
#         )
