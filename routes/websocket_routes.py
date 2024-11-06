from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import Depends, APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session
from services.auth_services import get_current_user
from services.db_services import get_db
from pydantic import BaseModel
from database.models import Device, Prediction, User, Zones
from services.socket_charts_service import manager
import random
import asyncio
import logging
import pytz

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

count_route = APIRouter()
realsocket_router = APIRouter()

class VisitorsCount(BaseModel):
    count: int
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


class RealTimeChartData(BaseModel):
    timestamp: datetime
    count: int



from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import random
import asyncio

@realsocket_router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    asia_manila_tz = pytz.timezone("Asia/Manila")
    await manager.connect(websocket)
    try:
        while True:
            random_limit = random.randint(10, 80)

            devices = db.query(Device).filter(
                Device.is_displayed == False
            ).limit(random_limit).all()
            
            estimated_count = len(devices)
            
            for prediction in devices:
                prediction.is_displayed = True
            
            db.commit()
            
            current_timestamp = datetime.now(asia_manila_tz).isoformat()
            payload = {
                "count": estimated_count,
                "timestamp": current_timestamp
            }
            
            await manager.broadcast(payload)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}")
    finally:
        manager.disconnect(websocket)




@count_route.get("/detail/count/staff", response_model=DetailsCount)
async def get_count_staff(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_count = db.query(User).filter(User.is_superuser == True).count()
    return DetailsCount(count=db_count, total_type="Total Staff")


@count_route.get("/detail/count/admin", response_model=DetailsCount)
async def get_count_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_count = db.query(User).filter(User.is_superuser == True).count()
    return DetailsCount(count=db_count, total_type="Total Admin")


@count_route.get("/detail/count/users", response_model=DetailsCount)
async def get_count_users(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    db_count = db.query(User).count()
    return DetailsCount(count=db_count, total_type="Total Users")


@count_route.get("/detail/count/section", response_model=DetailsCount)
async def get_count_section(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_count = db.query(Zones).count()
    return DetailsCount(count=db_count, total_type="Total Sections")


@count_route.get('/visitors/count/today/', response_model=VisitorsCount)
async def get_today_visitors_count_per_section(
    section_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
):
    total_count = db.query(
        func.coalesce(func.sum(Prediction.estimated_count), 0).label('total_count')
    ).filter(Prediction.zone_id == section_id).scalar()

    return VisitorsCount(
        count=total_count,
        analysis_type='Today Visitors'
    )

@count_route.get('/visitors/count/last-day/', response_model=VisitorsCount)
async def get_last_day_visitors_count_per_section(section_id: int, db: Session = Depends(get_db), current_user : User = Depends(get_current_user),):
    yesterday_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ) - timedelta(days=1)
    yesterday_end = yesterday_start + timedelta(days=1)

    count = (
        db.query(func.sum(Prediction.estimated_count))
        .filter(
            and_(
                Prediction.first_seen.between(yesterday_start, yesterday_end),
                Prediction.zone_id == section_id,
            ),
        )
        .scalar()
        or 0
    )

    return VisitorsCount(count=count, analysis_type="Last Day")

@count_route.get('/visitors/count/last-week/', response_model=VisitorsCount)
async def get_last_week_visitors_count_per_section(section_id: int, db: Session = Depends(get_db), current_user : User = Depends(get_current_user),):
    week_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ) - timedelta(days=7)
    today_end = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    count = (
        db.query(func.sum(Prediction.estimated_count))
        .filter(
            or_(
                Prediction.first_seen.between(week_start, today_end),
                Prediction.last_seen.between(week_start, today_end),
                and_(
                    Prediction.first_seen <= week_start,
                    Prediction.last_seen >= today_end,
                    Prediction.zone_id == section_id,
                ),
            )
        )
        .scalar()
        or 0
    )

    return VisitorsCount(count=count, analysis_type="Last Week")


@count_route.get('/visitors/count/last-month/', response_model=VisitorsCount)
async def get_last_month_visitors_count_per_section(section_id: int, db: Session = Depends(get_db), current_user : User = Depends(get_current_user),):
    month_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ) - timedelta(days=30)
    today_end = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    count = (
        db.query(func.sum(Prediction.estimated_count))
        .filter(
            or_(
                Prediction.first_seen.between(month_start, today_end),
                Prediction.last_seen.between(month_start, today_end),
                and_(
                    Prediction.first_seen <= month_start,
                    Prediction.last_seen >= today_end,
                    Prediction.zone_id == section_id,
                ),
            )
        )
        .scalar()
        or 0
    )

    return VisitorsCount(count=count, analysis_type="Last Month")


@count_route.get("/visitors/count/today", response_model=VisitorsCount)
async def get_visitors_count_today(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    today_end = today_start + timedelta(days=1)

    count = (
        db.query(func.sum(Prediction.estimated_count))
        .filter(
            or_(
                Prediction.first_seen.between(today_start, today_end),
                Prediction.last_seen.between(today_start, today_end),
                and_(
                    Prediction.first_seen <= today_start,
                    Prediction.last_seen >= today_end,
                ),
            )
        )
        .scalar()
        or 0
    )

    return VisitorsCount(count=count, analysis_type="Today")


@count_route.get("/visitors/count/last-day", response_model=VisitorsCount)
async def get_visitors_count_last_day(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    yesterday_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ) - timedelta(days=1)
    yesterday_end = yesterday_start + timedelta(days=1)

    count = (
        db.query(func.sum(Prediction.estimated_count))
        .filter(
            Prediction.first_seen.between(yesterday_start, yesterday_end),
        )
        .scalar()
        or 0
    )

    return VisitorsCount(count=count, analysis_type="Last Day")


@count_route.get("/visitors/count/last-week", response_model=VisitorsCount)
async def get_visitors_count_last_week(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    week_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ) - timedelta(days=7)
    today_end = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    count = (
        db.query(func.sum(Prediction.estimated_count))
        .filter(
            or_(
                Prediction.first_seen.between(week_start, today_end),
                Prediction.last_seen.between(week_start, today_end),
                and_(
                    Prediction.first_seen <= week_start,
                    Prediction.last_seen >= today_end,
                ),
            )
        )
        .scalar()
        or 0
    )

    return VisitorsCount(count=count, analysis_type="Last Week")


@count_route.get("/visitors/count/last-month", response_model=VisitorsCount)
async def get_visitors_count_last_month(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    month_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ) - timedelta(days=30)
    today_end = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    count = (
        db.query(func.sum(Prediction.estimated_count))
        .filter(
            or_(
                Prediction.first_seen.between(month_start, today_end),
                Prediction.last_seen.between(month_start, today_end),
                and_(
                    Prediction.first_seen <= month_start,
                    Prediction.last_seen >= today_end,
                ),
            )
        )
        .scalar()
        or 0
    )

    return VisitorsCount(count=count, analysis_type="Last Month")


@count_route.get(
    "/section/utilization", response_model=List[SectionUtilizationResponse]
)
async def get_section_utilization(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> List[SectionUtilizationResponse]:

    results = (
        db.query(
            Zones.name.label("section_name"),
            func.sum(Prediction.estimated_count).label("count"),
        )
        .join(Zones, Zones.id == Prediction.zone_id)
        .group_by(Zones.name)
        .all()
    )

    section_utilization = [
        SectionUtilizationResponse(section_name=section_name, count=count)
        for section_name, count in results
    ]

    return section_utilization


@count_route.get(
    "/time-series/per-day/visitors", response_model=List[TimeSeriesData]
)
async def get_time_series_visitors_day(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[TimeSeriesData]:
    result = (
        db.query(
            func.date(Prediction.first_seen).label("timestamp"),
            func.sum(Prediction.estimated_count).label("count"),
        )
        .group_by("timestamp")
        .order_by("timestamp")
        .all()
    )

    time_series_data = [
        TimeSeriesData(count=row.count, timestamp=row.timestamp) for row in result
    ]
    return time_series_data


@count_route.get(
    "/time-series/per-hour/visitors", response_model=List[TimeSeriesData]
)
async def get_time_series_visitors_hour(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[TimeSeriesData]:
    result = (
        db.query(
            func.date_format(Prediction.first_seen, "%Y-%m-%d %H:00:00").label(
                "timestamp"
            ),
            func.sum(Prediction.estimated_count).label("count"),
        )
        .group_by("timestamp")
        .order_by("timestamp")
        .all()
    )

    time_series_data = [
        TimeSeriesData(
            count=int(row.count),
            timestamp=datetime.strptime(row.timestamp, "%Y-%m-%d %H:%M:%S"),
        )
        for row in result
    ]
    return time_series_data
