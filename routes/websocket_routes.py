from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import WebSocket, Depends, APIRouter
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session
from services.db_services import get_db
from services.socket_charts_service import (
    manager,
)
from pydantic import BaseModel
from database.models import Prediction, User, Zones

websocket_router = APIRouter()


class VisitorsCount(BaseModel):
    count: str
    analysis_type: str


class DetailsCount(BaseModel):
    count: int
    total_type: str

class SectionUtilizationResponse(BaseModel):
    section_name: str
    count: int

class SectionVsSectionUtilizationResponse(BaseModel):
    section_name: str
    percentage: float


class TimeSeriesData(BaseModel):
    count: int
    timestamp: datetime

@websocket_router.get("/detail/count/staff", response_model=DetailsCount)
async def get_count_staff(db: Session = Depends(get_db)):
    db_count = db.query(User).filter(User.is_superuser == True).count()
    return DetailsCount(count=db_count, total_type="Total Staff")


@websocket_router.get("/detail/count/admin", response_model=DetailsCount)
async def get_count_admin(db: Session = Depends(get_db)):
    db_count = db.query(User).filter(User.is_superuser == True).count()
    return DetailsCount(count=db_count, total_type="Total Admin")


@websocket_router.get("/detail/count/users", response_model=DetailsCount)
async def get_count_users(db: Session = Depends(get_db)):
    db_count = db.query(User).count()
    return DetailsCount(count=db_count, total_type="Total Users")


@websocket_router.get("/detail/count/section", response_model=DetailsCount)
async def get_count_section(db: Session = Depends(get_db)):
    db_count = db.query(Zones).count()
    return DetailsCount(count=db_count, total_type="Total Sections")


@websocket_router.get("/visitors/count/today", response_model=VisitorsCount)
async def get_visitors_count_today(db: Session = Depends(get_db)):
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    count = (
        db.query(func.sum(Prediction.estimated_count))
        .filter(
            or_(
                Prediction.first_seen.between(today_start, today_end),
                Prediction.last_seen.between(today_start, today_end),
                and_(
                    Prediction.first_seen <= today_start,
                    Prediction.last_seen >= today_end
                )
            )
        )
        .scalar()
        or 0
    )

    formatted_count = f"{count / 1000:.1f}K" if count >= 1000 else str(count)

    return VisitorsCount(count=formatted_count, analysis_type="Today")

@websocket_router.get("/visitors/count/last-day", response_model=VisitorsCount)
async def get_visitors_count_last_day(db: Session = Depends(get_db)):
    yesterday_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    yesterday_end = yesterday_start + timedelta(days=1)

    count = (
        db.query(func.sum(Prediction.estimated_count))
        .filter(
            Prediction.first_seen.between(yesterday_start, yesterday_end),
        )
        .scalar()
        or 0
    )

    formatted_count = f"{count / 1000:.1f}K" if count >= 1000 else str(count)

    return VisitorsCount(count=formatted_count, analysis_type="Last Day")

@websocket_router.get("/visitors/count/last-week", response_model=VisitorsCount)
async def get_visitors_count_last_week(db: Session = Depends(get_db)):
    week_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
    today_end = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    count = (
        db.query(func.sum(Prediction.estimated_count))
        .filter(
            or_(
                Prediction.first_seen.between(week_start, today_end),
                Prediction.last_seen.between(week_start, today_end),
                and_(
                    Prediction.first_seen <= week_start,
                    Prediction.last_seen >= today_end
                )
            )
        )
        .scalar()
        or 0
    )

    formatted_count = f"{count / 1000:.1f}K" if count >= 1000 else str(count)

    return VisitorsCount(count=formatted_count, analysis_type="Last Week")

@websocket_router.get("/visitors/count/last-month", response_model=VisitorsCount)
async def get_visitors_count_last_month(db: Session = Depends(get_db)):
    month_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
    today_end = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    count = (
        db.query(func.sum(Prediction.estimated_count))
        .filter(
            or_(
                Prediction.first_seen.between(month_start, today_end),
                Prediction.last_seen.between(month_start, today_end),
                and_(
                    Prediction.first_seen <= month_start,
                    Prediction.last_seen >= today_end
                )
            )
        )
        .scalar()
        or 0
    )

    formatted_count = f"{count / 1000:.1f}K" if count >= 1000 else str(count)

    return VisitorsCount(count=formatted_count, analysis_type="Last Month")


@websocket_router.get('/section/utilization', response_model=List[SectionUtilizationResponse])
async def get_section_utilization(db: Session = Depends(get_db)) -> List[SectionUtilizationResponse]:
    
    results = (
        db.query(
            Zones.name.label("section_name"),
            func.sum(Prediction.estimated_count).label("count")
        )
        .join(Zones, Zones.id == Prediction.zone_id)
        .group_by(Zones.name)
        .all()
    )

    section_utilization = [SectionUtilizationResponse(section_name=section_name, count=count) for section_name, count in results]

    return section_utilization    


@websocket_router.get('/time-series/per-day/visitors', response_model=List[TimeSeriesData])
async def get_time_series_visitors_day(db: Session = Depends(get_db)) -> List[TimeSeriesData]:
    result = db.query(
        func.date(Prediction.first_seen).label('timestamp'),
        func.sum(Prediction.estimated_count).label('count')
    ).group_by('timestamp').order_by('timestamp').all()

    time_series_data = [TimeSeriesData(count=row.count, timestamp=row.timestamp) for row in result]
    return time_series_data


@websocket_router.get('/time-series/per-hour/visitors', response_model=List[TimeSeriesData])
async def get_time_series_visitors_hour(db: Session = Depends(get_db)) -> List[TimeSeriesData]:
    result = db.query(
        func.date_format(Prediction.first_seen, '%Y-%m-%d %H:00:00').label('timestamp'),
        func.sum(Prediction.estimated_count).label('count')
    ).group_by('timestamp').order_by('timestamp').all()

    time_series_data = [
        TimeSeriesData(count=int(row.count), timestamp=datetime.strptime(row.timestamp, '%Y-%m-%d %H:%M:%S'))
        for row in result
    ]
    return time_series_data
