from fastapi import APIRouter, Depends
from schema.prediction_schema import PredictionResponse
from typing import List
from sqlalchemy.orm import Session
from services.db_services import get_db
from database.database import User
from services.auth_services import get_current_user
from services.prediction_services import get_predictions

prediction_router = APIRouter()

@prediction_router.get("/predictions/", response_model=List[PredictionResponse])
def get_prediction(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[PredictionResponse]:
    return get_predictions(db=db)