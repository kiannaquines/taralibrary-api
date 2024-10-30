from fastapi import APIRouter, Depends, HTTPException, Query, status
from database.models import Prediction, Zones, Comment
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from routes.service_utils import (
    create_html_template,
    generate_feedback_chart,
    generate_peak_visitor_times_chart,
    generate_seaborn_chart,
    generate_time_spent_chart,
    generate_visitors_trends_chart,
    visitors_count_by_section_chart,
)
from services.db_services import get_db
from typing import List, Dict, Any
from sqlalchemy import func, and_
from io import BytesIO
import pdfkit
from pydantic import BaseModel
from sqlalchemy.orm import Session

class GenerateReportModel(BaseModel):
    start_date: datetime
    end_date: datetime

generate_report_router = APIRouter(tags=["Reports"])

def get_feedback_and_satisfaction(db: Session) -> List[Dict[str, Any]]:
    try:
        results = db.query(
            Zones.name.label("zone_name"),
            func.avg(Comment.rating).label("average_rating"),
            func.count(Comment.id).label("feedback_count"),
        ).join(Zones, Comment.zone_id == Zones.id) \
         .group_by(Zones.name) \
         .order_by(Zones.name).all()

        return [
            {
                "zone_name": r.zone_name,
                "average_rating": float(r.average_rating),
                "feedback_count": int(r.feedback_count),
            }
            for r in results
        ]
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching feedback and satisfaction data",
        )

def get_average_time_spent_in_zone(db: Session, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    try:
        results = db.query(
            Zones.name.label("zone_name"),
            func.avg(Prediction.scanned_minutes).label("average_time_spent"),
        ).join(Zones, Prediction.zone_id == Zones.id) \
         .filter(
             and_(
                 func.date(Prediction.first_seen) >= start_date,
                 func.date(Prediction.first_seen) < end_date,
             )
         ).group_by(Zones.name) \
         .order_by(Zones.name).all()

        return [
            {
                "zone_name": r.zone_name,
                "average_time_spent": float(r.average_time_spent),
            }
            for r in results
        ]
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while calculating average time spent in zone",
        )

def get_peak_visitor_times(db: Session, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    try:
        results = db.query(
            func.extract("hour", Prediction.first_seen).label("hour"),
            func.sum(Prediction.estimated_count).label("total_visits"),
        ).filter(
            and_(
                func.date(Prediction.first_seen) >= start_date,
                func.date(Prediction.first_seen) < end_date,
            )
        ).group_by(func.extract("hour", Prediction.first_seen)) \
         .order_by(func.extract("hour", Prediction.first_seen)).all()

        return [
            {"hour": int(r.hour), "total_visits": int(r.total_visits)} for r in results
        ]
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while retrieving peak visitor times.",
        )

def get_visitor_trends(db: Session, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    try:
        results = db.query(
            func.date(Prediction.first_seen).label("date"),
            func.sum(Prediction.estimated_count).label("total_visits"),
        ).filter(
            and_(
                func.date(Prediction.first_seen) >= start_date,
                func.date(Prediction.first_seen) < end_date,
            )
        ).group_by(func.date(Prediction.first_seen)) \
         .order_by(func.date(Prediction.first_seen)).all()

        return [
            {"date": r.date.strftime("%m-%d-%Y"), "total_visits": int(r.total_visits)}
            for r in results
        ]
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching visitor trends.",
        )

def get_daily_visitor_counts(db: Session, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    try:
        results = db.query(
            func.date_format(Prediction.first_seen, "%Y-%m-%d %H:%i").label("interval"),
            func.sum(Prediction.estimated_count).label("total_visits"),
        ).filter(
            and_(
                func.date(Prediction.first_seen) >= start_date,
                func.date(Prediction.first_seen) < end_date,
            )
        ).group_by(func.date_format(Prediction.first_seen, "%Y-%m-%d %H:%i")) \
         .order_by(func.date_format(Prediction.first_seen, "%Y-%m-%d %H:%i")).all()

        return [
            {"date": r.interval, "total_visits": int(r.total_visits)}
            for r in results
        ]
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching daily visitor counts.",
        )

def get_visitor_counts_by_section(db: Session, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    try:
        results = db.query(
            Zones.name.label("zone_name"),
            func.sum(Prediction.estimated_count).label("total_visits"),
        ).join(Zones, Prediction.zone_id == Zones.id) \
         .filter(
             and_(
                 func.date(Prediction.first_seen) >= start_date,
                 func.date(Prediction.first_seen) < end_date,
             )
         ).group_by(Zones.name) \
         .order_by(Zones.name).all()

        return [
            {"zone_name": r.zone_name, "total_visits": int(r.total_visits)}
            for r in results
        ]
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching visitor counts by section.",
        )

@generate_report_router.get(
    "/generate/report/daily",
    summary="Generate Daily Visitor Report",
    response_description="PDF report containing visitor statistics",
)
async def generate_pdf_report(
    start_date: str = Query(...),
    end_date: str = Query(...),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    try:

        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        daily_data = get_daily_visitor_counts(db, start_date, end_date)
        section_data = get_visitor_counts_by_section(db, start_date, end_date)
        peak_hours_data = get_peak_visitor_times(db, start_date, end_date)
        average_time_spent = get_average_time_spent_in_zone(db, start_date, end_date)
        feedback_satisfaction = get_feedback_and_satisfaction(db)
        trends_data = get_visitor_trends(db, start_date, end_date)

        if not daily_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No daily visitor data found",
            )

        line_chart_image = generate_seaborn_chart(daily_data)
        bar_chart_image = visitors_count_by_section_chart(section_data)
        chart_image = generate_visitors_trends_chart(trends_data)
        peak_hour_chart_image = generate_peak_visitor_times_chart(peak_hours_data)
        timespent_chart = generate_time_spent_chart(average_time_spent)
        feedback_chart = generate_feedback_chart(feedback_satisfaction)

        html_content = create_html_template(
            line_chart_image,
            bar_chart_image,
            chart_image,
            peak_hour_chart_image,
            timespent_chart,
            feedback_chart,
        )

        pdf_bytes = pdfkit.from_string(
            html_content,
            False,
            configuration=pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf'),
            options={
                "margin-top": "0.5in",
                "margin-right": "0.5in",
                "margin-bottom": "0.5in",
                "margin-left": "0.5in",
            },
        )

        pdf_filename = f"visitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={pdf_filename}"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
