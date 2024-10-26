from schema.chart_schema import *
from typing import List
from sqlalchemy.orm import Session, joinedload
from database.models import Prediction, Zones
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError


def get_all_predictions_score(db: Session) -> List[PredictionScore]:
    predictions = db.query(Prediction).options(joinedload(Prediction.zone)).all()

    try:
        return [
            PredictionScore(
                zone_name=prediction.zone.name,
                count=prediction.estimated_count,
                score=prediction.score,
            )
            for prediction in predictions
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch prediction score data",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, please try again.",
        )


def get_prediction_by_zone(db: Session, zone_id: int) -> List[PredictionScore]:
    predictions = (
        db.query(Prediction)
        .options(joinedload(Prediction.zone))
        .filter(Prediction.zone_id == zone_id)
    )

    check_existing_zone = db.query(Zones).filter(Zones.id == zone_id).first()

    if not check_existing_zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found"
        )

    try:
        return [
            PredictionScore(
                zone_name=prediction.zone.name,
                count=prediction.estimated_count,
                score=prediction.score,
            )
            for prediction in predictions
        ]

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Having an error in fetching prediction score data",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, please try again.",
        )


def get_all_estimated_count(db: Session) -> List[EstimatedCount]:
    estimated_count_result = (
        db.query(Prediction).options(joinedload(Prediction.zone)).all()
    )

    return [
        EstimatedCount(
            zone_name=count.zone.name,
            count=count.estimated_count,
        )
        for count in estimated_count_result
    ]


def get_estimated_count_by_zone(db: Session, zone_id: int) -> List[EstimatedCount]:
    estimated_count_result = (
        db.query(Prediction).options(joinedload(Prediction.zone)).filter(
            Prediction.zone_id == zone_id
        )
    )

    return [
        EstimatedCount(
            zone_name=count.zone.name,
            count=count.estimated_count,
        )
        for count in estimated_count_result
    ]
