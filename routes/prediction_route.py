from fastapi import APIRouter, Depends
from schema.prediction_schema import PredictionResponse
from typing import List
from sqlalchemy.orm import Session
from services.db_services import get_db
from database.models import User
from services.auth_services import get_current_user
from services.prediction_services import get_predictions, get_predictions_by_zone

prediction_router = APIRouter()

@prediction_router.get("/predictions/", response_model=List[PredictionResponse])
def get_prediction(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[PredictionResponse]:
    return get_predictions(db=db)


@prediction_router.get("/predictions/{zone_id}", response_model=List[PredictionResponse])
def get_prediction_by_zone_id(zone_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[PredictionResponse]:
    return get_predictions_by_zone(db=db, zone_id=zone_id)