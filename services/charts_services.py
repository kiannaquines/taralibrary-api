from schema.chart_schema import ChartData
from typing import List
from sqlalchemy.orm import Session

def get_all_charts(db: Session) -> List[ChartData]:
    pass

def get_charts_by_zone(db: Session, zone_id: int) -> List[ChartData]:
    pass