from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from services.db_services import get_db
from services.profile_services import (
    create_profile,
    get_profiles,
    get_profile,
    update_profile,
    delete_profile,
)
from schema.profile_schema import ProfileCreate, UpdateProfile, DeleteProfile
from typing import List
from database.database import User
from services.auth_services import get_current_user

profile_router = APIRouter()

@profile_router.post("/profiles/", response_model=ProfileCreate)
async def add_profile(
    profile_create: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_profile(db=db, current_user=current_user, profile_create=profile_create)
  


@profile_router.get("/profiles/", response_model=List[ProfileCreate])
async def view_profiles(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_profiles(db=db, skip=skip, limit=limit)


@profile_router.get("/profiles/{profile_id}", response_model=ProfileCreate)
async def view_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_profile = get_profile(db=db, current_user=current_user, profile_id=profile_id)
    if db_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return db_profile


@profile_router.put("/profiles/{profile_id}", response_model=UpdateProfile)
async def edit_profile(
    profile_id: int,
    profile_update: UpdateProfile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    
    return update_profile(db=db, profile_id=profile_id, current_user=current_user, profile=profile_update)

@profile_router.delete("/profiles/{profile_id}", response_model=DeleteProfile)
async def remove_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return delete_profile(db=db, current_user=current_user, profile_id=profile_id)
