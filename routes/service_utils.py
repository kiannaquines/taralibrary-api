import base64
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter, DayLocator
import pandas as pd
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams["font.family"] = "DejaVu Sans"

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
    
    ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M"))

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


def visitors_count_by_section_chart(section_data: List[Dict[str, Any]]) -> str:
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