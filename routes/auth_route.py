from fastapi import APIRouter, Depends
from schema.auth_schema import RegisterResponse, LoginResponse
from schema.user_schema import UserCreate
from schema.user_schema import UserResponse
from sqlalchemy.orm import Session
from services.auth_services import (
    get_current_user,
    authenticate_user, create_user,
)
from services.db_services import get_db
from database.database import User
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter()


@auth_router.post("/auth/register", response_model=RegisterResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(user=user, db=db)

@auth_router.post("/auth/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    return authenticate_user(form_data=form_data, db=db)


@auth_router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
