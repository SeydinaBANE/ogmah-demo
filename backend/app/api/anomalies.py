from datetime import date
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.ml.anomaly_detector import AnomalyDetector

router = APIRouter(prefix="/api/anomalies", tags=["anomalies"])

_detector = AnomalyDetector()


class AnomalyOut(BaseModel):
    purchase_id: int
    ingredient_name: str
    supplier: str
    purchase_date: date
    unit_price: float
    rolling_avg_price: float
    price_deviation_pct: float
    anomaly_score: float


@router.get("/", response_model=list[AnomalyOut])
def get_anomalies(
    days: int = Query(default=30, ge=1, le=180),
    db: Session = Depends(get_db),
):
    """Detect and return anomalous purchases over the last N days."""
    results = _detector.detect(db, days_back=days)
    return [AnomalyOut(
        purchase_id=r.purchase_id,
        ingredient_name=r.ingredient_name,
        supplier=r.supplier,
        purchase_date=r.purchase_date,
        unit_price=r.unit_price,
        rolling_avg_price=r.rolling_avg_price,
        price_deviation_pct=r.price_deviation_pct,
        anomaly_score=r.anomaly_score,
    ) for r in results]


@router.post("/retrain")
def retrain(db: Session = Depends(get_db)):
    """Re-fit the anomaly model on all available purchase data."""
    _detector.fit(db)
    return {"status": "model retrained"}
