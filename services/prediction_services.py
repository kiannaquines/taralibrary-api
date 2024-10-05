from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import List
from schema.prediction_schema import PredictionResponse
from database.database import Prediction


def get_predictions(db: Session) -> List[PredictionResponse]:
    response = db.query(Prediction).all()
    
    if not response:
    
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No predictions found"
        )

    try:

        return [
            PredictionResponse(
                id=prediction.id,
                zone_id=prediction.zone_id,
                estimated_count=prediction.estimated_count,
                first_seen=prediction.first_seen,
                last_seen=prediction.last_seen,
                scanned_minutes=prediction.scanned_minutes,
            )
            for prediction in response
        ]

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get predictions: {str(e)}",
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )