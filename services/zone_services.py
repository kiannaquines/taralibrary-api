import uuid
import os
import shutil
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from schema.chart_schema import ChartDataResponse
from database.models import Zones, ZoneImage, Comment, Prediction, Category
from sqlalchemy.exc import SQLAlchemyError
from fastapi import UploadFile, status
from config.settings import ZONE_UPLOAD_DIRECTORY, DIR_UPLOAD_ZONE_IMG
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
    CategoryResponse
)
from schema.comment_schema import CommentViewResponse
from statistics import mean
from sqlalchemy import func


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
    zone: ZoneCreate,
    files: Optional[List[UploadFile]] = None,
) -> ZoneResponse:
    db_zone = db.query(Zones).filter(Zones.id == zone_id).first()

    if not db_zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found"
        )

    try:
        for key, value in zone.dict(exclude_unset=True).items():
            setattr(db_zone, key, value)

        db.commit()
        db.refresh(db_zone)

        if files:
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
                    ZoneImageResponse(id=zone_image.id, image_url=zone_image.image_url)
                )

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
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")


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
                    raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error occurred while deleting image: {str(e)}"
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
    zone = (
        db.query(Zones)
        .filter(Zones.id == zone_id)
        .options(joinedload(Zones.predictions))
        .options(joinedload(Zones.comment_related))
        .options(joinedload(Zones.categories))
        .options(joinedload(Zones.images))
        .first()
    )

    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found",
        )

    try:
        total_rating = (
            round(mean(rating.rating for rating in zone.comment_related), 2)
            if zone.comment_related
            else 0.0
        )

        return ZoneInfoResponse(
            id=zone.id,
            name=zone.name,
            description=zone.description,
            comments=(
                [
                    CommentViewResponse(
                        id=comment.id,
                        zone_id=comment.zone_id,
                        first_name=comment.user.first_name,
                        last_name=comment.user.last_name,
                        comment=comment.comment,
                        rating=comment.rating,
                        date_added=comment.date_added,
                        update_date=comment.update_date,
                    )
                    for comment in zone.comment_related
                ]
                if zone.comment_related
                else []
            ),
            images=(
                [
                    ZoneImageResponse(
                        id=image.id,
                        zone_id=image.zone_id,
                        image_url=f"/static/{DIR_UPLOAD_ZONE_IMG}/{image.image_url}",
                    )
                    for image in zone.images
                ]
                if zone.images
                else []
            ),
            predictions=(
                [
                    ChartDataResponse(
                        count=prediction.estimated_count,
                        time=prediction.first_seen.strftime("%I:%M %p"),
                    )
                    for prediction in zone.predictions
                ]
                if zone.predictions
                else []
            ),
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
            Zones, func.avg(Comment.rating).label("average_rating"), ZoneImage.image_url
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
        return "Moderate Attendance"


def get_recommended_zones_service(db: Session) -> List[RecommendSectionResponse]:
    query_recommended_zones = (
        db.query(
            Zones,
            func.coalesce(func.avg(Comment.rating), 0.0).label("average_rating"),
            ZoneImage.image_url,
            func.count(Prediction.estimated_count).label("estimated_count"),
        )
        .outerjoin(Comment)
        .outerjoin(Prediction)
        .outerjoin(ZoneImage)
        .group_by(Zones.id)
        .order_by(func.count(Prediction.estimated_count).desc())
        .options(joinedload(Zones.predictions))
        .all()
    )

    return [
        RecommendSectionResponse(
            section_id=popular_zone.id,
            status=classify_zone(estimated_count),
            section_name=popular_zone.name,
            description=" ".join(popular_zone.description.split()[:7]),
            total_rating=round(average_rating, 2),
            image_url=(
                f"/static/{DIR_UPLOAD_ZONE_IMG}/{image_url}" if image_url else None
            ),
        )
        for popular_zone, average_rating, image_url, estimated_count in query_recommended_zones
    ]


def get_all_section_section_filters(db: Session) -> List[AllSectionResponse]:
    query_all_sections = (
        db.query(
            Zones,
            func.coalesce(func.avg(Comment.rating), 0.0).label("average_rating"),
            ZoneImage.image_url,
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
            ]
        )
        for popular_zone, average_rating, image_url in query_all_sections
    ]


def get_all_zones(db: Session) -> List[AllSectionWebApi]:
    zones = (
        db.query(Zones)
        .options(joinedload(Zones.images))
        .all()
    )

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
                update_date=zone.update_date
            )
        )

    return zone_responses