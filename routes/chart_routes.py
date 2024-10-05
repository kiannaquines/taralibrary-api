from fastapi import APIRouter, Depends
from schema.chart_schema import ChartData
from typing import List
from services.charts_services import get_all_charts, get_charts_by_zone
from sqlalchemy.orm import Session
from services.auth_services import get_current_user
from services.db_services import get_db

charts_router = APIRouter()


@charts_router.get("/chart/", response_model=List[ChartData])
async def get_charts(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> List[ChartData]:
    return get_all_charts(db=db)


@charts_router.get("/chart/{zone_id}", response_model=List[ChartData])
async def get_charts_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> List[ChartData]:
    return get_charts_by_zone(db=db, zone_id=zone_id)
