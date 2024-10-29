from typing import List
from fastapi import APIRouter, Depends, UploadFile, File
from schema.auth_schema import *
from schema.user_schema import (
    AddUserResponse, UserDeleteResponse, UserUpdateResponse, UsersListResponse
)
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
    username: str,
    email: EmailStr,
    first_name: str,
    last_name: str,
    is_superuser: bool,
    is_verified: bool,
    is_staff: bool,
    is_active: bool,
    db: Session = Depends(get_db),
    profile_img: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
):
    try:
        if profile_img:
            return update_user(
                db=db,
                user_id=user_id,
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_superuser=is_superuser,
                is_verified=is_verified,
                is_staff=is_staff,
                is_active=is_active,
                profile_img=profile_img,
            )
        else:
            return update_user(
                db=db,
                user_id=user_id,
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_superuser=is_superuser,
                is_verified=is_verified,
                is_staff=is_staff,
                is_active=is_active,
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")
        