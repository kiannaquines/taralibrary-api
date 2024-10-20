from typing import List
from fastapi import APIRouter, Depends
from config.settings import DIR_UPLOAD_PROFILE_IMG
from schema.auth_schema import *
from schema.user_schema import AddUserResponse, UserDeleteResponse, UserResponse, UserUpdate, UserUpdateResponse, UsersListResponse
from sqlalchemy.orm import Session
from services.auth_services import *
from services.db_services import get_db
from services.users_services import add_user, delete_user, get_users, update_user
from database.models import User

users_router = APIRouter()

@users_router.post("/users/add", response_model=AddUserResponse)
def user_add(
    user_details: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return add_user(db=db, user=user_details)


@users_router.get("/users/list", response_model=List[UsersListResponse])
def users_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_users(db=db)


@users_router.delete("/users/remove", response_model=UserDeleteResponse)
def users_remove(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_user(db=db, userId=user_id)


@users_router.put("/users/edit", response_model=UserUpdateResponse)
def update_user_account(
    user_id: int,
    user_detail: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserUpdateResponse:
    return update_user(db=db, user_id=user_id, user_detail=user_detail)
