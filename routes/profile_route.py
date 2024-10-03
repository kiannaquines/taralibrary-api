from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from services.db_services import get_db
from services.profile_services import (
    create_profile,
    get_profiles,
    get_profile,
    update_profile,
    delete_profile,
)
from schema.profile_schema import ProfileCreate
from typing import List

profile_router = APIRouter()

@profile_router.post("/profiles/", response_model=ProfileCreate)
async def add_profile(
    profile_create: ProfileCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_profile(db=db, profile_create=profile_create)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create profile")


@profile_router.get("/profiles/", response_model=List[ProfileCreate])
async def view_profiles(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return get_profiles(db=db, skip=skip, limit=limit)


@profile_router.get("/profiles/{profile_id}", response_model=ProfileCreate)
async def view_profile(
    profile_id: int,
    db: Session = Depends(get_db),
):
    db_profile = get_profile(db=db, profile_id=profile_id)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_profile


@profile_router.put("/profiles/{profile_id}", response_model=ProfileCreate)
async def edit_profile(
    profile_id: int,
    profile_update: ProfileCreate,
    db: Session = Depends(get_db),
):
    db_profile = update_profile(db=db, profile_id=profile_id, profile=profile_update)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return ProfileCreate(
        user_id=db_profile.user_id,
        year=db_profile.year,
        college=db_profile.college,
        course=db_profile.course,
    )


@profile_router.delete("/profiles/{profile_id}", response_model=ProfileCreate)
async def remove_profile(
    profile_id: int,
    db: Session = Depends(get_db),
):
    db_profile = delete_profile(db=db, profile_id=profile_id)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_profile
