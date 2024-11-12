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
import json

# realtime chart
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
# count staff
@count_route.get("/detail/count/staff", response_model=DetailsCount)
async def get_count_staff(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_count = db.query(User).filter(User.is_superuser == True).count()
    return DetailsCount(count=db_count, total_type="Total Staff")
# count admin
@count_route.get("/detail/count/admin", response_model=DetailsCount)
async def get_count_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_count = db.query(User).filter(User.is_superuser == True).count()
    return DetailsCount(count=db_count, total_type="Total Admin")
# count users
@count_route.get("/detail/count/users", response_model=DetailsCount)
async def get_count_users(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    db_count = db.query(User).count()
    return DetailsCount(count=db_count, total_type="Total Users")
# count section
@count_route.get("/detail/count/section", response_model=DetailsCount)
async def get_count_section(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_count = db.query(Zones).count()
    return DetailsCount(count=db_count, total_type="Total Sections")

# dashboard
@count_route.get("/visitors/count/last-month", response_model=VisitorsCount)
async def get_visitors_count_last_month(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    month_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ) - timedelta(days=30)
    today_end = datetime.now(timezone.utc).replace(
        hour=23, minute=59, second=59, microsecond=999999
    )

    subquery_probe_request = (
        db.query(Device.device_addr)
        .filter(
            and_(
                Device.date_detected >= month_start,
                Device.date_detected < today_end,
                Device.frame_type == "Probe Request"
            )
        )
        .group_by(Device.device_addr)
        .having(func.count(Device.device_addr) > 25)
        .subquery()
    )

    subquery_other_frame = (
        db.query(Device.device_addr)
        .filter(
            and_(
                Device.date_detected >= month_start,
                Device.date_detected < today_end,
                Device.frame_type != "Probe Request"
            )
        )
        .group_by(Device.device_addr)
        .subquery()
    )


    count = (
        db.query(func.coalesce(func.count(func.distinct(Device.device_addr)), 0))
        .filter(
            or_(
                Device.device_addr.in_(subquery_probe_request),
                Device.device_addr.in_(subquery_other_frame)
            )
        )
        .scalar()
        or 0
    )

    return VisitorsCount(count=count, analysis_type="Last Month")

# dashboard
@count_route.get("/visitors/count/last-day", response_model=VisitorsCount)
async def get_visitors_count_last_day(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    yesterday_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ) - timedelta(days=1)
    yesterday_end = yesterday_start + timedelta(days=1)

    subquery_probe_request = (
        db.query(Device.device_addr)
        .filter(
            and_(
                Device.date_detected >= yesterday_start,
                Device.date_detected < yesterday_end,
                Device.frame_type == "Probe Request"
            )
        )
        .group_by(Device.device_addr)
        .having(func.count(Device.device_addr) > 25)
        .subquery()
    )

    subquery_other_frame = (
        db.query(Device.device_addr)
        .filter(
            and_(
                Device.date_detected >= yesterday_start,
                Device.date_detected < yesterday_end,
                Device.frame_type != "Probe Request"
            )
        )
        .group_by(Device.device_addr)
        .subquery()
    )


    count = (
        db.query(func.coalesce(func.count(func.distinct(Device.device_addr)), 0))
        .filter(
            or_(
                Device.device_addr.in_(subquery_probe_request),
                Device.device_addr.in_(subquery_other_frame)
            )
        )
        .scalar()
        or 0
    )

    return VisitorsCount(count=count, analysis_type="Last Day")
# dashboard
@count_route.get("/visitors/count/last-week", response_model=VisitorsCount)
async def get_visitors_count_last_week(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    week_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ) - timedelta(days=7)
    today_end = datetime.now(timezone.utc).replace(
        hour=23, minute=59, second=59, microsecond=999999
    )

    subquery_probe_request = (
        db.query(Device.device_addr)
        .filter(
            and_(
                Device.date_detected >= week_start,
                Device.date_detected < today_end,
                Device.frame_type == "Probe Request"
            )
        )
        .group_by(Device.device_addr)
        .having(func.count(Device.device_addr) > 25)
        .subquery()
    )

    subquery_other_frame = (
        db.query(Device.device_addr)
        .filter(
            and_(
                Device.date_detected >= week_start,
                Device.date_detected < today_end,
                Device.frame_type != "Probe Request"
            )
        )
        .group_by(Device.device_addr)
        .subquery()
    )


    count = (
        db.query(func.coalesce(func.count(func.distinct(Device.device_addr)), 0))
        .filter(
            or_(
                Device.device_addr.in_(subquery_probe_request),
                Device.device_addr.in_(subquery_other_frame)
            )
        )
        .scalar()
        or 0
    )

    return VisitorsCount(count=count, analysis_type="Last Week")
# dashboard
@count_route.get("/visitors/count/today", response_model=VisitorsCount)
async def get_visitors_count_today(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    
    today_end = today_start + timedelta(days=1)

    subquery_probe_request = (
        db.query(Device.device_addr)
        .filter(
            and_(
                Device.date_detected >= today_start,
                Device.date_detected < today_end,
                Device.frame_type == "Probe Request"
            )
        )
        .group_by(Device.device_addr)
        .having(func.count(Device.device_addr) > 25)
        .subquery()
    )

    subquery_other_frame = (
        db.query(Device.device_addr)
        .filter(
            and_(
                Device.date_detected >= today_start,
                Device.date_detected < today_end,
                Device.frame_type != "Probe Request"
            )
        )
        .group_by(Device.device_addr)
        .subquery()
    )


    count = (
        db.query(func.coalesce(func.count(func.distinct(Device.device_addr)), 0))
        .filter(
            or_(
                Device.device_addr.in_(subquery_probe_request),
                Device.device_addr.in_(subquery_other_frame)
            )
        )
        .scalar()
        or 0
    )

    return VisitorsCount(count=count, analysis_type="Today")

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
