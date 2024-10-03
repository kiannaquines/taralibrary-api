from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from services.db_services import (
    get_db
)
from services.profile_services import (
    create_profile,
    get_profiles,
    get_profile,
    update_profile,
    delete_profile,
)
from schemas import (
    ProfileCreate,
    Profile,
) 
from typing import List


profile_router = APIRouter()

@profile_router.post("/profiles/", response_model=Profile)
def add_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    return create_profile(db=db, profile=profile)

@profile_router.get("/profiles/", response_model=List[Profile])
def view_profiles(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_profiles(db=db, skip=skip, limit=limit)

@profile_router.get("/profiles/{profile_id}", response_model=Profile)
def view_profile(profile_id: int, db: Session = Depends(get_db)):
    db_profile = get_profile(db=db, profile_id=profile_id)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_profile

@profile_router.put("/profiles/{profile_id}", response_model=Profile)
def edit_profile(profile_id: int, profile: ProfileCreate, db: Session = Depends(get_db)):
    db_profile = update_profile(db=db, profile_id=profile_id, profile=profile)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_profile

@profile_router.delete("/profiles/{profile_id}", response_model=Profile)
def remove_profile(profile_id: int, db: Session = Depends(get_db)):
    db_profile = delete_profile(db=db, profile_id=profile_id)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_profile