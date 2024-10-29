from datetime import date, datetime, timedelta
import uuid
import os
import shutil
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from schema.chart_schema import ChartDataResponse
from database.models import Zones, ZoneImage, Comment, Prediction, Category
from sqlalchemy.exc import SQLAlchemyError
from fastapi import UploadFile, status
from config.settings import ZONE_UPLOAD_DIRECTORY, DIR_UPLOAD_ZONE_IMG, DIR_UPLOAD_PROFILE_IMG
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from schema.zone_schema import (
    AllSectionResponse,
    AllSectionWebApi,
    ZoneInfoResponse,
    PopularSectionResponse,
    RecommendSectionResponse,
    ZoneCreate,
    ZoneResponse,
    ZoneImageResponse,
    ZoneRemoved,
    CategoryResponse,
    ZoneUpdate,
)
from schema.comment_schema import CommentViewResponse
from statistics import mean
from sqlalchemy import and_, case, func


def create_zone(
    db: Session,
    zone: ZoneCreate,
    files: List[UploadFile],
) -> ZoneResponse:
    db_zone = Zones(name=zone.name, description=zone.description)

    try:
        db.add(db_zone)
        db.commit()
        db.refresh(db_zone)

        image_responses = []
        for file in files:
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            file_location = os.path.join(ZONE_UPLOAD_DIRECTORY, unique_filename)

            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            zone_image = ZoneImage(image_url=unique_filename, zone_id=db_zone.id)
            db.add(zone_image)
            db.commit()

            image_responses.append(
                ZoneImageResponse(
                    id=zone_image.id,
                    image_url=f"/static/{DIR_UPLOAD_ZONE_IMG}/{zone_image.image_url}",
                )
            )

        return ZoneResponse(
            id=db_zone.id,
            name=db_zone.name,
            description=db_zone.description,
            images=image_responses,
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")


def get_zones(db: Session, skip: int = 0, limit: int = 10) -> List[ZoneResponse]:
    zones = (
        db.query(Zones)
        .options(joinedload(Zones.images))
        .offset(skip)
        .limit(limit)
        .all()
    )

    if not zones:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No zones found"
        )

    zone_responses = []
    for zone in zones:
        zone_responses.append(
            ZoneResponse(
                id=zone.id,
                name=zone.name,
                description=zone.description,
                images=[
                    ZoneImageResponse(
                        id=image.id,
                        image_url=f"/static/{DIR_UPLOAD_ZONE_IMG}/{image.image_url}",
                    )
                    for image in zone.images
                ],
            )
        )

    return zone_responses


def get_zone(db: Session, zone_id: int) -> ZoneResponse:
    zone = (
        db.query(Zones)
        .filter(Zones.id == zone_id)
        .options(joinedload(Zones.images))
        .first()
    )

    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found"
        )

    return ZoneResponse(
        id=zone.id,
        name=zone.name,
        description=zone.description,
        images=[
            ZoneImageResponse(
                id=image.id,
                image_url=f"/static/{DIR_UPLOAD_ZONE_IMG}/{image.image_url}",
            )
            for image in zone.images
        ],
    )


def update_zone(
    db: Session,
    zone_id: int,
    zone: ZoneUpdate,
    files: Optional[List[UploadFile]] = None,
) -> ZoneResponse:

    from database.models import zone_category_association

    db_zone = db.query(Zones).filter(Zones.id == zone_id).first()
    if not db_zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found"
        )

    try:

        db.begin_nested()

        if zone.name is not None:
            db_zone.name = zone.name
        if zone.description is not None:
            db_zone.description = zone.description

        if zone.categories is not None:

            existing_category_ids = {
                assoc.category_id
                for assoc in db.query(zone_category_association)
                .filter(zone_category_association.c.zone_id == zone_id)
                .all()
            }

            new_category_ids = {cat.category_id for cat in zone.categories}

            for existing_id in existing_category_ids:
                if existing_id not in new_category_ids:
                    db.query(zone_category_association).filter(
                        zone_category_association.c.zone_id == zone_id,
                        zone_category_association.c.category_id == existing_id,
                    ).delete()

            for category_data in zone.categories:

                if category_data.category_id in existing_category_ids:
                    continue

                category = (
                    db.query(Category)
                    .filter(Category.id == category_data.category_id)
                    .first()
                )
                if not category:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Category with id {category_data.category_id} not found",
                    )

                new_association = zone_category_association.insert().values(
                    zone_id=zone_id, category_id=category_data.category_id
                )

                db.execute(new_association)

        db.commit()

        if files:
            for file in files:
                try:
                    if not file.content_type.startswith("image/"):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File {file.filename} is not an image",
                        )

                    unique_filename = f"{uuid.uuid4()}_{file.filename}"
                    file_location = os.path.join(ZONE_UPLOAD_DIRECTORY, unique_filename)

                    os.makedirs(ZONE_UPLOAD_DIRECTORY, exist_ok=True)

                    with open(file_location, "wb+") as buffer:
                        shutil.copyfileobj(file.file, buffer)

                    zone_image = ZoneImage(
                        image_url=unique_filename, zone_id=db_zone.id
                    )
                    db.add(zone_image)
                    db.flush()

                except Exception as e:
                    print(f"Error processing file {file.filename}: {str(e)}")
                    continue

            db.commit()

        db.refresh(db_zone)

        return ZoneResponse(
            id=db_zone.id,
            name=db_zone.name,
            description=db_zone.description,
            images=[
                ZoneImageResponse(
                    id=image.id,
                    image_url=f"/static/{DIR_UPLOAD_ZONE_IMG}/{image.image_url}",
                )
                for image in db_zone.images
            ],
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


def delete_zone(db: Session, zone_id: int) -> ZoneRemoved | None:
    db_zone = db.query(Zones).filter(Zones.id == zone_id).first()

    if not db_zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found",
        )

    try:
        db.delete(db_zone)
        db.commit()

        for image in db_zone.images:
            image_path = os.path.join(ZONE_UPLOAD_DIRECTORY, image.image_url)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except OSError as e:
                    raise HTTPException(
                        status_code=500, detail=f"Failed to delete image: {str(e)}"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error occurred while deleting image: {str(e)}",
                )

            db.delete(image)
            db.commit()

        return ZoneRemoved(
            message="You have successfully removed the zone",
            is_deleted=True,
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_info_zone_service(db: Session, zone_id: int) -> ZoneInfoResponse:
    current_day = date.today()
    
    try:
        zone = (
            db.query(Zones)
            .filter(Zones.id == zone_id)
            .options(
                joinedload(Zones.predictions),
                joinedload(Zones.comment_related),
                joinedload(Zones.categories),
                joinedload(Zones.images),
            )
            .first()
        )

        if not zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Zone not found",
            )

        total_rating = round(mean(rating.rating for rating in zone.comment_related), 2) if zone.comment_related else 0.0

        sorted_predictions = sorted(
            zone.predictions,
            key=lambda prediction: prediction.first_seen,
            reverse=True
        )

        return ZoneInfoResponse(
            id=zone.id,
            name=zone.name,
            description=zone.description,
            comments=[
                CommentViewResponse(
                    id=comment.id,
                    zone_id=comment.zone_id,
                    first_name=comment.user.first_name,
                    last_name=comment.user.last_name,
                    profile_img=f"/static/{DIR_UPLOAD_PROFILE_IMG}/{comment.user.profile_img}",
                    comment=comment.comment,
                    rating=comment.rating,
                    date_added=comment.date_added.strftime("%m/%d/%Y"),
                    update_date=comment.update_date.strftime("%m/%d/%Y"),
                )
                for comment in zone.comment_related
            ] if zone.comment_related else [],
            images=[
                ZoneImageResponse(
                    id=image.id,
                    zone_id=image.zone_id,
                    image_url=f"/static/{DIR_UPLOAD_ZONE_IMG}/{image.image_url}",
                )
                for image in zone.images
            ] if zone.images else [],
            predictions=[
                ChartDataResponse(
                    count=prediction.estimated_count,
                    time=prediction.first_seen.strftime("%I:%M %p"),
                )
                for prediction in sorted_predictions
                if prediction.first_seen.date() == current_day
            ] if sorted_predictions else [],
            total_rating=total_rating,
            total_reviews=len(zone.comment_related),
        )

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Something went wrong while fetching zone information: {e}",
        )

def get_popular_zones_service(db: Session) -> List[PopularSectionResponse]:
    query_popular_zones = (
        db.query(
            Zones,
            func.avg(Comment.rating).label("average_rating"),
            func.min(ZoneImage.image_url).label("image_url")
        )
        .outerjoin(Comment)
        .outerjoin(ZoneImage)
        .group_by(Zones.id)
        .order_by(func.avg(Comment.rating).desc())
        .options(joinedload(Zones.comment_related))
        .all()
    )

    return [
        PopularSectionResponse(
            section_id=popular_zone.id,
            section_name=popular_zone.name,
            total_rating=round(avg_rating, 2) if avg_rating is not None else 0.0,
            image_url=(
                f"/static/{DIR_UPLOAD_ZONE_IMG}/{image_url}" if image_url else None
            ),
        )
        for popular_zone, avg_rating, image_url in query_popular_zones
    ]


def classify_zone(estimated_count: int) -> str:
    CONGESTED_THRESHOLD = 50
    SPACIOUS_THRESHOLD = 10

    if estimated_count >= CONGESTED_THRESHOLD:
        return "Congested"
    elif estimated_count <= SPACIOUS_THRESHOLD:
        return "Spacious"
    else:
        return "Moderate"


def get_recommended_zones_service(db: Session) -> List[RecommendSectionResponse]:
    current_datetime = datetime.now()
    current_hour = current_datetime.replace(minute=0, second=0, microsecond=0)

    query_recommended_zones = (
        db.query(
            Zones,
            func.coalesce(func.avg(Comment.rating), 0.0).label("average_rating"),
            func.max(ZoneImage.image_url).label("image_url"),
            func.count(
                case(
                    (
                        and_(
                            Prediction.first_seen >= current_hour,
                            Prediction.first_seen < current_hour + timedelta(hours=1)
                        ),
                        Prediction.estimated_count
                    )
                )
            ).label("current_hour_count"),
        )
        .outerjoin(Comment)
        .outerjoin(Prediction)
        .outerjoin(ZoneImage)
        .group_by(Zones.id)
        .order_by(Zones.id)
        .options(joinedload(Zones.predictions))
        .all()
    )

    return [
        RecommendSectionResponse(
            section_id=zone.id,
            status=classify_zone(current_hour_count),
            section_name=zone.name,
            description=" ".join(zone.description.split()[:7]),
            total_rating=round(average_rating, 2),
            image_url=(
                f"/static/{DIR_UPLOAD_ZONE_IMG}/{image_url}" if image_url else None
            ),
        )
        for zone, average_rating, image_url, current_hour_count in query_recommended_zones
    ]


def get_all_section_section_filters(db: Session) -> List[AllSectionResponse]:
    query_all_sections = (
        db.query(
            Zones,
            func.coalesce(func.avg(Comment.rating), 0.0).label("average_rating"),
            func.max(ZoneImage.image_url).label('image_url'),
        )
        .outerjoin(Comment)
        .outerjoin(ZoneImage)
        .group_by(Zones.id)
        .all()
    )

    return [
        AllSectionResponse(
            section_id=popular_zone.id,
            section_name=popular_zone.name,
            description=" ".join(popular_zone.description.split()[:7]),
            total_rating=round(average_rating, 2),
            image_url=(
                f"/static/{DIR_UPLOAD_ZONE_IMG}/{image_url}" if image_url else None
            ),
            categories=[
                CategoryResponse(
                    category_name=category.category,
                )
                for category in popular_zone.categories
            ],
        )
        for popular_zone, average_rating, image_url in query_all_sections
    ]


def get_all_zones(db: Session) -> List[AllSectionWebApi]:
    zones = db.query(Zones).options(joinedload(Zones.images)).all()

    if not zones:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No zones found"
        )

    zone_responses = []
    for zone in zones:
        zone_responses.append(
            AllSectionWebApi(
                id=zone.id,
                name=zone.name,
                description=zone.description,
                image_url=[
                    ZoneImageResponse(
                        id=image.id,
                        image_url=f"/static/{DIR_UPLOAD_ZONE_IMG}/{image.image_url}",
                    )
                    for image in zone.images
                ],
                categories=[
                    CategoryResponse(
                        category_name=category.category,
                    )
                    for category in zone.categories
                ],
                date_added=zone.date_added,
                update_date=zone.update_date,
            )
        )

    return zone_responses


class VisitorCounts(BaseModel):
    count: int
    analysis_type: str 

class VisitorsOverTime(BaseModel):
    timestamp: datetime
    count: int

class AllInfoCount(BaseModel):
    count: List[VisitorCounts]
    data_overtime: List[VisitorsOverTime]

def get_data_per_section(db: Session, section_id: int) -> AllInfoCount:
    fetch_data = db.query(Prediction).filter(Prediction.zone_id == section_id).all()
    return fetch_data