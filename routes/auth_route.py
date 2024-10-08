from fastapi import APIRouter, Depends
from schema.auth_schema import *
from schema.user_schema import UserCreate
from schema.user_schema import UserResponse
from sqlalchemy.orm import Session
from services.auth_services import *
from services.db_services import get_db
from database.database import User
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter()


@auth_router.post("/auth/register", response_model=RegisterResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    return await create_user(user=user, db=db)


@auth_router.post("/auth/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    return authenticate_user(form_data=form_data, db=db)


@auth_router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@auth_router.post("/auth/register/verify", response_model=SuccessVerification)
def verify_user_account(
    verification_data: VerificationRequest, db: Session = Depends(get_db)
):
    return verify_account_code(verification_data=verification_data, db=db)


@auth_router.post("/auth/request/forgot-password", response_model=SuccessVerification)
def forgot_password(
    password_request_change_data: RequestChangePassword, db: Session = Depends(get_db)
):
    return reset_password(
        password_request_change_data=password_request_change_data, db=db
    )


@auth_router.post("/auth/request/change-password", response_model=SuccessVerification)
def change_password_email(
    change_password_data: ChangePassword, db: Session = Depends(get_db)
):
    return change_password(db=db, change_password_data=change_password_data)
