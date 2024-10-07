from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import List
from schema.prediction_schema import PredictionResponse
from database.database import Prediction


def get_predictions(db: Session) -> List[PredictionResponse]:
    predictions = db.query(Prediction).all()

    if not predictions:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No predictions found"
        )

    try:

        return [
            PredictionResponse(
                id=prediction.id,
                zone_id=prediction.zone_id,
                estimated_count=prediction.estimated_count,
                score=prediction.score,
                first_seen=prediction.first_seen,
                last_seen=prediction.last_seen,
                scanned_minutes=prediction.scanned_minutes,
            )
            for prediction in predictions
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


def get_predictions_by_zone(db: Session, zone_id: int) -> List[PredictionResponse]:
    prediction_result = db.query(Prediction).filter(Prediction.zone_id == zone_id).all()

    if not prediction_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No predictions found for zone with id {zone_id}",
        )
    
    try:
        return [
            PredictionResponse(
                id=prediction.id,
                zone_id=prediction.zone_id,
                estimated_count=prediction.estimated_count,
                score=prediction.score,
                first_seen=prediction.first_seen,
                last_seen=prediction.last_seen,
                scanned_minutes=prediction.scanned_minutes,
            )
            for prediction in prediction_result
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get predictions for zone with id {zone_id}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )