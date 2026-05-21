from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Sale, Recipe

router = APIRouter(prefix="/api/sales", tags=["sales"])


class DailySaleOut(BaseModel):
    sale_date: date
    total_revenue: float
    total_covers: int


class KPIOut(BaseModel):
    monthly_revenue: float
    monthly_covers: int
    daily_avg_revenue: float
    daily_avg_covers: float


@router.get("/daily", response_model=list[DailySaleOut])
def daily_sales(
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
):
    cutoff = date.today() - timedelta(days=days)
    rows = db.execute(
        select(Sale.sale_date, func.sum(Sale.revenue), func.sum(Sale.quantity_sold))
        .where(Sale.sale_date >= cutoff)
        .group_by(Sale.sale_date)
        .order_by(Sale.sale_date)
    ).fetchall()
    return [DailySaleOut(
        sale_date=r[0], total_revenue=float(r[1]), total_covers=int(r[2])
    ) for r in rows]


@router.get("/kpi", response_model=KPIOut)
def get_kpi(db: Session = Depends(get_db)):
    month_start = date.today().replace(day=1)

    month_data = db.execute(
        select(func.sum(Sale.revenue), func.sum(Sale.quantity_sold))
        .where(Sale.sale_date >= month_start)
    ).one()

    days_elapsed = (date.today() - month_start).days + 1
    return KPIOut(
        monthly_revenue=float(month_data[0] or 0),
        monthly_covers=int(month_data[1] or 0),
        daily_avg_revenue=float(month_data[0] or 0) / days_elapsed,
        daily_avg_covers=float(month_data[1] or 0) / days_elapsed,
    )
