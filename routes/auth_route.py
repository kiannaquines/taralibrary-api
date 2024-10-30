from fastapi import APIRouter, Depends, File, Form, UploadFile
from config.settings import DIR_UPLOAD_PROFILE_IMG
from schema.auth_schema import *
from schema.user_schema import UserCreate
from sqlalchemy.orm import Session
from services.auth_services import *
from services.db_services import get_db
from database.models import User
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter()



@auth_router.post("/auth/register", response_model=RegisterResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    return await create_user(user=user, db=db)

@auth_router.post("/auth/admin/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    return admin_authenticate_user(form_data=form_data, db=db)

@auth_router.post("/auth/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    return authenticate_user(form_data=form_data, db=db)

from pydantic import BaseModel, EmailStr

class UserResponseData(BaseModel):
    id: int
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    profile_img: str
    is_superuser: bool
    is_staff: bool
    is_active: bool

@auth_router.get("/users/me", response_model=UserResponseData)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserResponseData(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        profile_img=f"/static/{DIR_UPLOAD_PROFILE_IMG}/{current_user.profile_img}",
        is_superuser=current_user.is_superuser,
        is_staff=current_user.is_staff,
        is_active=current_user.is_active,
    )


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


@auth_router.put("/users/me/update", response_model=UpdateProfile)
def update_profile_route(
    user_id: int,
    current_user: str = Depends(get_current_user),
    email: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    profile_img: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    try:
        profile = UpdateProfile(
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_id=user_id,
        )

        return update_profile_service(
            db=db,
            update_profile_data=profile,
            profile_img=profile_img,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error occurred: {str(e)}",
        )


@auth_router.put("/users/me/change-password", response_model=SuccessVerification)
def change_password_in_account(
    change_password_data: ChangePasswordInAccount,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return change_password_in_account_service(db=db, change_password_data=change_password_data)
