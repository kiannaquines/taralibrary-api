from fastapi import APIRouter, Depends, File, UploadFile, Form, status
from sqlalchemy.orm import Session
from services.db_services import get_db
from services.zone_services import (
    create_zone,
    get_all_section_section_filters,
    get_all_zones,
    get_popular_zones_service,
    get_recommended_zones_service,
    get_section_count_analysis,
    get_zone,
    get_zones,
    update_zone,
    delete_zone,
    get_info_zone_service,
)
from schema.zone_schema import (
    AllSectionResponse,
    AllSectionWebApi,
    RecommendSectionResponse,
    ZoneCategoryUpdate,
    ZoneResponse,
    ZoneCreate,
    ZoneRemoved,
    ZoneInfoResponse,
    PopularSectionResponse,
    ZoneUpdate,
)
from typing import List, Optional
from fastapi.exceptions import HTTPException
from database.models import User
from services.auth_services import get_current_user

zone_router = APIRouter()


@zone_router.get("/zones/", response_model=List[ZoneResponse])
async def view_zones(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_zones(db=db, skip=skip, limit=limit)


@zone_router.get("/zones/all", response_model=List[AllSectionResponse])
async def view_zones(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_all_section_section_filters(db=db)


@zone_router.post("/zones/", response_model=ZoneResponse)
async def add_zone(
    name: str = Form(...),
    description: str = Form(...),
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    zone = ZoneCreate(name=name, description=description)
    return create_zone(db=db, zone=zone, files=files)


@zone_router.get("/zones/{zone_id}", response_model=ZoneResponse)
async def view_zone_details(
    zone_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_zone = get_zone(db=db, zone_id=zone_id)
    if db_zone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found"
        )
    return db_zone


@zone_router.put("/zones/{zone_id}", response_model=ZoneResponse)
async def edit_zone(
    zone_id: int,
    name: str = Form(...),
    description: str = Form(...),
    categories_json: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
):
    try:
        categories = None
        if categories_json:
            category_ids = [
                int(id.strip()) for id in categories_json.split(",") if id.strip()
            ]
            categories = [
                ZoneCategoryUpdate(category_id=cat_id) for cat_id in category_ids
            ]

        zone_update_data = ZoneUpdate(
            name=name, description=description, categories=categories
        )

        db_zone = update_zone(
            db=db, zone_id=zone_id, zone=zone_update_data, files=files
        )
        return db_zone

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category IDs must be valid integers",
        )


@zone_router.delete("/zones/{zone_id}", response_model=ZoneRemoved)
async def remove_zone(
    zone_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_zone = delete_zone(db=db, zone_id=zone_id)
    return db_zone


@zone_router.get("/zones/info/{zone_id}", response_model=ZoneInfoResponse)
def get_info_zone(
    zone_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_info_zone_service(db=db, zone_id=zone_id)


@zone_router.get("/zones/popular/", response_model=List[PopularSectionResponse])
def get_popular_zones(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_popular_zones_service(db=db)


@zone_router.get("/zones/recommended/", response_model=List[RecommendSectionResponse])
def get_recommended_zones(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_recommended_zones_service(db=db)


@zone_router.get("/web/zones/all", response_model=List[AllSectionWebApi])
async def view_zones(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_all_zones(db=db)



@zone_router.get('/zones/info/count/section/{sectionId}')
def get_todays_section_count(
    sectionId: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return get_section_count_analysis(db=db, sectionId=sectionId)
