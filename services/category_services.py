from sqlalchemy.orm import Session
from database.models import Category, User
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


def category_remove(db: Session, category_id: int) -> RemoveCategoryResponse:
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    try:
        db.delete(category)
        db.commit()
        return RemoveCategoryResponse(message="Category deleted successfully")

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete category: {str(e)}",
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete category",
        )


def category_update(
    db: Session, category_id: int, category_data: CategoryCreate
) -> CategoryResponse:
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    category.category = category_data.category_name
    db.commit()
    db.refresh(category)

    return CategoryResponse(
        category_id=category.id,
        category_name=category.category,
        date_added=category.date_added,
        update_date=category.update_date,
    )
