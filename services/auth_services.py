from datetime import datetime, timedelta
import os
import shutil
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, UploadFile, status
from jose import JWTError, jwt
from config.settings import SECRET_KEY, ALGORITHM, PROFILE_UPLOAD_DIRECTORY
from database.models import User, VerificationCode
from services.db_services import get_db, oauth2_scheme, pwd_context
from fastapi.security import OAuth2PasswordRequestForm
from config.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from schema.auth_schema import *
from schema.user_schema import UserCreate
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from services.send_email_services import (
    send_email,
    account_verification_email_body,
    account_password_reset_email_body,
)


def authenticate_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password must be provided",
        )

    try:
        user = db.query(User).filter(User.username == form_data.username).first()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed {e}",
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User still not verified yet",
        )

    try:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user.username,
                "verified": user.is_verified,
                "is_superuser": user.is_superuser,
            },
            expires_delta=access_token_expires,
        )
        return LoginResponse(access_token=access_token, token_type="bearer")

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to authenticate user due to a database error {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to authenticate user due to an unexpected error {str(e)}",
        )


async def create_user(user: UserCreate, db: Session = Depends(get_db)):

    if user.password != user.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )

    db_user = (
        db.query(User)
        .filter(or_(User.username == user.username, User.email == user.email))
        .first()
    )

    if db_user:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or Email is already taken",
        )

    try:

        hashed_password = get_password_hash(user.confirm_password)
        new_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        user_success = RegisterSuccess(
            id=new_user.id,
            email=new_user.email,
            username=new_user.username,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
        )

        body = account_verification_email_body(db=db)

        sent_email_status = send_email(
            receiver_email=new_user.email,
            subject="Account Verification",
            body=body,
        )

        if not sent_email_status:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email",
            )

        return RegisterResponse(
            message="Verification code has been sent to your email.",
            user=user_success,
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred {str(e)}",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}",
        )


async def logout_user(user: User, db: Session = Depends(get_db)):
    pass


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_current_user(current_user_id: int, profile_creation_user_id: int) -> bool:
    return current_user_id == profile_creation_user_id


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_account_code(
    verification_data: VerificationRequest, db: Session
) -> SuccessVerification:

    if len(verification_data.code) > 6 or len(verification_data.code) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code should be a 6-digit number",
        )

    verify_user = db.query(User).filter(User.id == verification_data.user_id)
    used_code = db.query(VerificationCode).filter(
        VerificationCode.code == verification_data.code
    )

    if not verify_user.first() or not used_code.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification code or user not found",
        )
        
    if used_code.first().is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has already been used",
        )


    verify_user.first().is_verified = True
    used_code.first().is_used = True
    db.commit()

    return SuccessVerification(message="You have successfully verified your account", user_id=verify_user.first().id)


def reset_password(
    db: Session, password_request_change_data: RequestChangePassword
) -> SuccessVerification:
    db_user = (
        db.query(User).filter(User.email == password_request_change_data.email).first()
    )

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cannot find your email address",
        )

    body = account_password_reset_email_body(
        db=db,
        email=db_user.email,
    )

    send_email_request = send_email(
        receiver_email=db_user.email,
        subject="Password Reset Request",
        body=body,
    )

    if not send_email_request:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send password reset email",
        )

    return SuccessVerification(message="Password reset request sent successfully", user_id=db_user.id)


def change_password(db: Session, change_password_data: ChangePassword):

    if change_password_data.new_password != change_password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirm password do not match",
        )

    db_user = db.query(User).filter(User.id == change_password_data.user_id).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db_user.hashed_password = get_password_hash(change_password_data.new_password)
    db.commit()
    db.refresh(db_user)

    return SuccessVerification(message="Password has been changed successfully", user_id=db_user.id)


def update_profile_service(
    db: Session,
    update_profile_data: UpdateProfile,
    profile_img: UploadFile = None,
):
    user = db.query(User).filter(User.id == update_profile_data.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        if profile_img:
            filename = profile_img.filename
            image_path = f"{PROFILE_UPLOAD_DIRECTORY}/{filename}"
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(profile_img.file, buffer)
            user.profile_img = filename

        user.email = update_profile_data.email
        user.first_name = update_profile_data.first_name
        user.last_name = update_profile_data.last_name

        db.commit()
        db.refresh(user)

        return UpdateProfile(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            user_id=user.id,
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    
def change_password_in_account_service(db: Session, change_password_data: ChangePasswordInAccount):

    if change_password_data.new_password != change_password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirm password do not match",
        )

    db_user = db.query(User).filter(User.id == change_password_data.user_id).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not verify_password(change_password_data.old_password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Old password is incorrect",
        )
    

    db_user.hashed_password = get_password_hash(change_password_data.confirm_password)
    db.commit()
    db.refresh(db_user)

    return SuccessVerification(message="Password has been changed successfully", user_id=db_user.id)

