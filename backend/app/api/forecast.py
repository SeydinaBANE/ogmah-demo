from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.ml.demand_forecaster import DemandForecaster

router = APIRouter(prefix="/api/forecast", tags=["forecast"])

_forecaster = DemandForecaster()


class ForecastPointOut(BaseModel):
    forecast_date: date
    predicted_qty: float
    lower_bound: float
    upper_bound: float


class ForecastOut(BaseModel):
    recipe_id: int
    recipe_name: str
    model_rmse: float
    forecast: list[ForecastPointOut]


@router.get("/{recipe_id}", response_model=ForecastOut)
def get_forecast(
    recipe_id: int,
    days: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db),
):
    result = _forecaster.forecast(db, recipe_id, days)
    if result is None:
        raise HTTPException(status_code=404, detail="Recipe not found or insufficient data")
    return ForecastOut(
        recipe_id=result.recipe_id,
        recipe_name=result.recipe_name,
        model_rmse=result.model_rmse,
        forecast=[ForecastPointOut(**vars(p)) for p in result.forecast],
    )
