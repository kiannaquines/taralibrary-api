from fastapi import APIRouter, Depends, File, Form, UploadFile
from config.settings import DIR_UPLOAD_PROFILE_IMG
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
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        profile_img=f'/static/{DIR_UPLOAD_PROFILE_IMG}/{current_user.profile_img}',
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
