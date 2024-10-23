import os
from pydantic import EmailStr
from sqlalchemy.orm import Session
from config.settings import PROFILE_UPLOAD_DIRECTORY
from database.models import User
from fastapi import File, HTTPException, UploadFile, status
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from services.auth_services import get_password_hash
from schema.user_schema import (
    AddUserResponse,
    UserCreate,
    UserDeleteResponse,
    UserUpdate,
    UserUpdateResponse,
    UsersListResponse,
)


def add_user(db: Session, user: UserCreate) -> AddUserResponse:

    if user.password != user.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )

    db_check_username = db.query(User).filter(User.username == user.username).first()
    db_check_email = db.query(User).filter(User.email == user.email).first()

    if db_check_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    if db_check_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        first_name=user.first_name,
        last_name=user.last_name,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return AddUserResponse(
        message="User added successfully",
    )


def get_users(db: Session) -> List[UsersListResponse]:

    response = db.query(User).all()

    if not response:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found",
        )

    try:

        return [
            UsersListResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_superuser=user.is_superuser,
                is_verified=user.is_verified,
                profile_img=user.profile_img,
                register_date=user.register_date,
                update_date=user.update_date,
            )
            for user in response
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}",
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}",
        )


def delete_user(db: Session, userId: int) -> UserDeleteResponse:

    response = db.query(User).filter(User.id == userId).first()

    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found",
        )

    try:
        db.delete(response)
        db.commit()

        return UserDeleteResponse(
            message="User deleted successfully",
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}",
        )


def update_user(
    db: Session,
    user_id: int,
    username: str,
    email: EmailStr,
    first_name: str,
    last_name: str,
    is_superuser: bool,
    is_verified: bool,
    is_staff: bool,
    is_active: bool,
    profile_img: UploadFile = File(None),
) -> UserUpdateResponse:

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.is_superuser = is_superuser
        user.is_verified = is_verified
        user.is_staff = is_staff
        user.is_active = is_active

        if profile_img:
            file_location = os.path.join(PROFILE_UPLOAD_DIRECTORY, profile_img.filename)

            with open(file_location, "wb") as buffer:
                buffer.write(profile_img.file.read())
            
            user.profile_img = profile_img.filename

        db.commit()
        db.refresh(user)

        return UserUpdateResponse(
            message="User updated successfully",
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}",
        )
