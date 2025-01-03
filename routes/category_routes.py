from fastapi import APIRouter, Depends
from schema.category_schema import *
from typing import List
from services.category_services import *
from sqlalchemy.orm import Session
from services.auth_services import get_current_user
from services.db_services import get_db

category_router = APIRouter()


@category_router.post("/category/", response_model=CategoryResponse)
async def add_category_route(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> CategoryResponse:
    return add_category(
        db=db,
        category_data=category_data,
    )


@category_router.get("/category/", response_model=List[CategoryResponse])
async def get_prediction_all(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> List[CategoryResponse]:
    return get_categories(db=db)


@category_router.delete("/category/", response_model=RemoveCategoryResponse)
async def remove_category(
    catId: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> RemoveCategoryResponse:
    return category_remove(db=db, category_id=catId)



@category_router.put("/category/", response_model=CategoryResponse)
async def remove_category(
    category_id: int,
    category_data : CategoryCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> CategoryResponse:
    return category_update(db=db, category_id=category_id, category_data=category_data)

