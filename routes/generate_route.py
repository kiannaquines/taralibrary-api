from fastapi import APIRouter, Depends, HTTPException, status
from database.models import Prediction, Zones, Comment
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from services.db_services import get_db
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import matplotlib.pyplot as plt
from sqlalchemy import func
from io import BytesIO
import seaborn as sns
import pandas as pd
import pdfkit
import base64
import os

sns.set_style("whitegrid")
plt.rcParams["font.family"] = "DejaVu Sans"

generate_report_router = APIRouter(tags=["Reports"])


async def get_feedback_and_satisfaction(db: Session) -> List[Dict[str, Any]]:
    try:
        results = (
            db.query(
                Zones.name.label("zone_name"),
                func.avg(Comment.rating).label("average_rating"),
                func.count(Comment.id).label("feedback_count"),
            )
            .join(Zones, Comment.zone_id == Zones.id)
            .group_by(Zones.name)
            .order_by(Zones.name)
            .all()
        )
        return [
            {
                "zone_name": r.zone_name,
                "average_rating": float(r.average_rating),
                "feedback_count": int(r.feedback_count),
            }
            for r in results
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred feedback and satisfaction data",
        )


def generate_feedback_chart(feedback_data: List[Dict[str, Any]]) -> str:
    plt.clf()
    df = pd.DataFrame(feedback_data)

    fig, ax = plt.subplots(figsize=(10, 6))
    bar_plot = sns.barplot(
        data=df, x="zone_name", y="average_rating", hue="zone_name", palette="Blues", ax=ax, legend=False,
    )

    plt.title("Average Feedback Ratings by Zone", pad=10, fontsize=12)
    plt.xlabel("Zone Name", labelpad=8, fontsize=10)
    plt.ylabel("Average Rating (1-5)", labelpad=8, fontsize=10)
    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png", dpi=210, bbox_inches="tight")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return image_base64


async def get_average_time_spent_in_zone(db: Session) -> List[Dict[str, Any]]:
    try:
        results = (
            db.query(
                Zones.name.label("zone_name"),
                func.avg(Prediction.scanned_minutes).label("average_time_spent"),
            )
            .join(Zones, Prediction.zone_id == Zones.id)
            .group_by(Zones.name)
            .order_by(Zones.name)
            .all()
        )
        return [
            {
                "zone_name": r.zone_name,
                "average_time_spent": float(r.average_time_spent),
            }
            for r in results
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred average time spent in zone",
        )


def generate_time_spent_chart(zone_data: List[Dict[str, Any]]) -> str:
    plt.clf()
    df = pd.DataFrame(zone_data)

    fig, ax = plt.subplots(figsize=(10, 6))
    bar_plot = sns.barplot(
        data=df, x="zone_name", y="average_time_spent", hue="zone_name", palette="Blues", ax=ax, legend=False,
    )

    plt.title("Average Time Spent in Each Zone", pad=10, fontsize=12)
    plt.xlabel("Zone Name", labelpad=8, fontsize=10)
    plt.ylabel("Average Time Spent (minutes)", labelpad=8, fontsize=10)
    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png", dpi=210, bbox_inches="tight")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return image_base64


async def get_peak_visitor_times(db: Session) -> List[Dict[str, Any]]:
    try:
        results = (
            db.query(
                func.extract("hour", Prediction.first_seen).label("hour"),
                func.sum(Prediction.estimated_count).label("total_visits"),
            )
            .group_by(func.extract("hour", Prediction.first_seen))
            .order_by(func.extract("hour", Prediction.first_seen))
            .all()
        )
        return [
            {"hour": int(r.hour), "total_visits": int(r.total_visits)} for r in results
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred peak hour visitors.",
        )


def generate_peak_visitor_times_chart(peak_data: List[Dict[str, Any]]) -> str:
    plt.clf()
    df = pd.DataFrame(peak_data)

    fig, ax = plt.subplots(figsize=(10, 6))
    bar_plot = sns.barplot(data=df, x="hour", y="total_visits", hue="hour", palette="Blues", ax=ax, legend=False,)

    plt.title("Peak Visitor Times", pad=10, fontsize=12)
    plt.xlabel("Hour of Day", labelpad=8, fontsize=10)
    plt.ylabel("Total Visits", labelpad=8, fontsize=10)
    plt.xticks(rotation=0, fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png", dpi=210, bbox_inches="tight")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return image_base64


async def get_visitor_trends(
    db: Session, start_date: datetime, end_date: datetime
) -> List[Dict[str, Any]]:
    try:
        results = (
            db.query(
                func.date(Prediction.first_seen).label("date"),
                func.sum(Prediction.estimated_count).label("total_visits"),
            )
            .group_by(func.date(Prediction.first_seen))
            .order_by(func.date(Prediction.first_seen))
            .all()
        )
        
        return [
            {"date": r.date.strftime("%m-%d-%Y"), "total_visits": int(r.total_visits)}
            for r in results
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred: {str(e)}",
        )

    
from matplotlib.dates import DateFormatter, DayLocator

def generate_visitors_trends_chart(trends_data: List[Dict[str, Any]]) -> str:
    plt.clf()
    df = pd.DataFrame(trends_data)
    df["date"] = pd.to_datetime(df["date"])

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(
        data=df,
        x="date",
        y="total_visits",
        linewidth=2,
        color="#1f77b4",
        label="Total Visits",
    )

    plt.title("Visitors Trends Over Time", pad=10, fontsize=12)
    plt.xlabel("Date", labelpad=8, fontsize=10)
    plt.ylabel("Total Visits", labelpad=8, fontsize=10)
    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(fontsize=8)

    ax.xaxis.set_major_locator(DayLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%m-%d-%Y"))

    plt.tight_layout()
    plt.legend(title="Visitor Count")

    buffer = BytesIO()
    plt.savefig(buffer, format="png", dpi=210, bbox_inches="tight")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return image_base64


async def get_daily_visitor_counts(db: Session) -> List[Dict[str, Any]]:
    try:
        results = (
            db.query(
                func.date_format(Prediction.first_seen, "%Y-%m-%d %H:%i").label("interval"),  # Format to date and time
                func.sum(Prediction.estimated_count).label("total_visits"),
            )
            .group_by(func.date_format(Prediction.first_seen, "%Y-%m-%d %H:%i"))  # Group by the same interval
            .order_by(func.date_format(Prediction.first_seen, "%Y-%m-%d %H:%i"))
            .all()
        )
        return [
            {"date": r.interval, "total_visits": int(r.total_visits)}
            for r in results
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching 30-minute visitor counts.",
        )


async def get_visitor_counts_by_section(db: Session) -> List[Dict[str, Any]]:
    try:
        results = (
            db.query(
                Zones.name.label("zone_name"),
                func.sum(Prediction.estimated_count).label("total_visits"),
            )
            .join(Zones, Prediction.zone_id == Zones.id)
            .group_by(Zones.name)
            .order_by(Zones.name)
            .all()
        )
        return [
            {"zone_name": r.zone_name, "total_visits": int(r.total_visits)}
            for r in results
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred visitor counts by section.",
        )


def generate_seaborn_chart(half_hourly_data: List[Dict[str, Any]]) -> str:
    plt.clf()
    df = pd.DataFrame(half_hourly_data)
    df["date"] = pd.to_datetime(df["date"])

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(
        data=df,
        x="date",
        y="total_visits",
        linewidth=2,
        color="#1f77b4",
        label="Total Visits",
    )

    plt.title("Visitor Counts Every 30 Minutes", pad=10, fontsize=12)
    plt.xlabel("Date and Time", labelpad=8, fontsize=10)
    plt.ylabel("Total Visits", labelpad=8, fontsize=10)
    
    ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M"))  # Format for 30-minute intervals

    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    plt.legend(title="Visitor Count")

    buffer = BytesIO()
    plt.savefig(buffer, format="png", dpi=210, bbox_inches="tight")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return image_base64


def generate_bar_chart(section_data: List[Dict[str, Any]]) -> str:
    plt.clf()
    df = pd.DataFrame(section_data)

    fig, ax = plt.subplots(figsize=(10, 6))

    bar_plot = sns.barplot(
        data=df, x="zone_name", y="total_visits", hue="zone_name", palette="Blues", ax=ax, legend=False,
    )

    plt.title("Visitor Counts by Section", pad=10, fontsize=12)
    plt.xlabel("Zone Name", labelpad=8, fontsize=10)
    plt.ylabel("Total Visits", labelpad=8, fontsize=10)
    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()

    plt.legend(title="Zone Names", labels=df["zone_name"].tolist(), loc="upper right")

    buffer = BytesIO()
    plt.savefig(buffer, format="png", dpi=210, bbox_inches="tight")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return image_base64


def create_html_template(
    line_chart_base64: str,
    bar_chart_base64: str,
    trending_chart_base64: str,
    peakhour_chart_base64: str,
    feedback_satisfaction_base64: str,
    timespent_chart_base64: str,
) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Visitor Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                line-height: 1.6;
                color: #343a40;
            }}
            .container {{
                width: 100%;
                margin: auto;
                background: white;
                padding: 20px;
                border-radius: 8px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 20px;
                border-bottom: 2px solid #1f77b4;
                padding-bottom: 10px;
            }}
            .header h1 {{
                font-size: 30px;
                margin: 0;
                color: #1f77b4;
            }}
            .header span {{
                font-size: 20px;
                color: #666;
            }}
            .chart-container {{
                text-align: center;
                margin: 20px 0;
            }}
            .chart-container img {{
                width: 100%;
                max-width: 100%;
                height: auto; 
                display: block;
                margin: 0 auto;
                border: 1px solid #dee2e6;
                border-radius: 5px;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                color: #666;
                font-size: 20px;
                border-top: 1px solid #dee2e6;
                padding-top: 10px;
            }}
            @media print {{
                .container {{
                    box-shadow: none;
                    border-radius: 0;
                }}
                .footer {{
                    page-break-after: always;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Kundo E. Pham Learning Resource Center</h1>
                <span>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            </div>
            <div class="chart-container">
                <img src="data:image/png;base64,{line_chart_base64}" alt="Daily Visitor Chart">
                <br>
                <img src="data:image/png;base64,{bar_chart_base64}" alt="Visitor Counts by Section">
                <br>
                <img src="data:image/png;base64,{trending_chart_base64}" alt="Trend Analysis">
                <br>
                <img src="data:image/png;base64,{peakhour_chart_base64}" alt="Peak Hours">
                <br>
                <img src="data:image/png;base64,{feedback_satisfaction_base64}" alt="Feedback Satisfaction">
                <br>
                <img src="data:image/png;base64,{timespent_chart_base64}" alt="Time Spent">
            </div>
            <div class="footer">
                <p>This report was automatically generated. For any queries, please contact the administration.</p>
            </div>
        </div>
    </body>
    </html>
    """



@generate_report_router.get(
    "/generate/report/daily",
    summary="Generate Daily Visitor Report",
    response_description="PDF report containing visitor statistics",
)
async def generate_pdf_report(db: Session = Depends(get_db)) -> StreamingResponse:
    try:
        daily_data = await get_daily_visitor_counts(db)
        section_data = await get_visitor_counts_by_section(db)
        peak_hours_data = await get_peak_visitor_times(db)

        average_time_spent = await get_average_time_spent_in_zone(db)
        feedback_satisfaction = await get_feedback_and_satisfaction(db)

        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        trends_data = await get_visitor_trends(db, start_date, end_date)

        if not daily_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No daily visitor data found",
            )

        line_chart_image = generate_seaborn_chart(daily_data)
        bar_chart_image = generate_bar_chart(section_data)
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
            configuration=pdfkit.configuration(
                wkhtmltopdf='/usr/local/bin/wkhtmltopdf'
            ),
            options={
                "margin-top": "15mm",
                "margin-right": "15mm",
                "margin-bottom": "15mm",
                "margin-left": "15mm",
                "encoding": "UTF-8",
                "page-size": "A3",
                "dpi": 300,
            },
        )

        pdf_filename = f"visitor_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        response = StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={pdf_filename}"},
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}",
        )
