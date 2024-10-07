from fastapi import APIRouter, Depends
from schema.chart_schema import *
from typing import List
from services.charts_services import *
from sqlalchemy.orm import Session
from services.auth_services import get_current_user
from services.db_services import get_db

charts_router = APIRouter()


@charts_router.get("/chart/predictions/score", response_model=List[PredictionScore])
async def get_prediction_all(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> List[PredictionScore]:
    return get_all_predictions_score(db=db)


@charts_router.get(
    "/chart/predictions/score/zone/{zone_id}", response_model=List[PredictionScore]
)
async def get_predictiom_by_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> List[PredictionScore]:
    return get_prediction_by_zone(db=db, zone_id=zone_id)


@charts_router.get("/chart/predictions/estimated/", response_model=List[EstimatedCount])
async def get_prediction_estimated_count(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> List[EstimatedCount]:
    return get_all_estimated_count(db=db)


@charts_router.get(
    "/chart/predictions/estimated/zone/{zone_id}", response_model=List[EstimatedCount]
)
async def get_prediction_estimated_count(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> List[EstimatedCount]:
    return get_estimated_count_by_zone(db=db, zone_id=zone_id)
