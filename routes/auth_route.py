from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
from schemas import UserCreate, UserInDB, RegisterResponse, LoginRequest, LoginResponse
from sqlalchemy.orm import Session
from services.auth_services import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)
from services.db_services import (
    get_db
)
from database import User
from settings import ACCESS_TOKEN_EXPIRE_MINUTES

auth_router = APIRouter()


@auth_router.post("/auth/register", response_model=RegisterResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")

        hashed_password = get_password_hash(user.password)
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

        user_response = UserCreate(
            email=new_user.email,
            username=new_user.username,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            password=user.password,
        )

        return RegisterResponse(
            message="User registered successfully", user=user_response
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@auth_router.post("/auth/login", response_model=LoginResponse)
async def login(form_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user:
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

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return LoginResponse(access_token=access_token, token_type="bearer")


@auth_router.get("/users/me", response_model=UserInDB)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user