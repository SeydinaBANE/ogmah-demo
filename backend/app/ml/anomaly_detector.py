"""
Detects anomalous ingredient purchase prices using Isolation Forest.
Compares each purchase against the rolling 30-day average for that ingredient.
"""
from dataclasses import dataclass
from datetime import date, timedelta

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import settings
from app.models.db_models import Purchase, Ingredient

MODEL_PATH = f"{settings.model_dir}/anomaly_model.joblib"


@dataclass
class AnomalyResult:
    purchase_id: int
    ingredient_name: str
    supplier: str
    purchase_date: date
    unit_price: float
    rolling_avg_price: float
    price_deviation_pct: float
    anomaly_score: float
    is_anomaly: bool


class AnomalyDetector:
    def __init__(self, contamination: float = 0.03):
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=100,
            random_state=42,
        )
        self._fitted = False

    def _load_purchase_df(self, db: Session, days_back: int = 180) -> pd.DataFrame:
        cutoff = date.today() - timedelta(days=days_back)
        rows = db.execute(
            select(
                Purchase.id,
                Purchase.ingredient_id,
                Purchase.purchase_date,
                Purchase.unit_price,
                Purchase.supplier,
                Ingredient.name.label("ingredient_name"),
            )
            .join(Ingredient)
            .where(Purchase.purchase_date >= cutoff)
            .order_by(Purchase.purchase_date)
        ).fetchall()

        return pd.DataFrame(rows, columns=[
            "id", "ingredient_id", "purchase_date", "unit_price", "supplier", "ingredient_name"
        ])

    def _compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["purchase_date"] = pd.to_datetime(df["purchase_date"])
        df["unit_price"] = df["unit_price"].astype(float)

        df = df.sort_values(["ingredient_id", "purchase_date"])

        # Rolling 30-purchase average price per ingredient (baseline for anomaly detection)
        df["rolling_avg"] = (
            df.groupby("ingredient_id")["unit_price"]
            .transform(lambda x: x.rolling(window=30, min_periods=1).mean().shift(1))
        )
        df["rolling_avg"] = df["rolling_avg"].fillna(df["unit_price"])

        df["price_ratio"] = df["unit_price"] / df["rolling_avg"]
        df["price_deviation_pct"] = (df["price_ratio"] - 1) * 100

        # Log-ratio as main anomaly feature (robust to scale differences across ingredients)
        df["log_ratio"] = np.log(df["price_ratio"].clip(lower=0.01))

        return df

    def fit(self, db: Session) -> "AnomalyDetector":
        df = self._load_purchase_df(db)
        if df.empty:
            return self
        features = self._compute_features(df)
        X = features[["log_ratio"]].values
        self.model.fit(X)
        self._fitted = True
        joblib.dump(self.model, MODEL_PATH)
        return self

    def detect(self, db: Session, days_back: int = 30) -> list[AnomalyResult]:
        """Run anomaly detection on recent purchases."""
        if not self._fitted:
            # Try loading persisted model, else fit on the fly
            try:
                self.model = joblib.load(MODEL_PATH)
                self._fitted = True
            except FileNotFoundError:
                self.fit(db)

        # Load full history for rolling stats, then filter to recent window
        full_df = self._load_purchase_df(db, days_back=180)
        if full_df.empty:
            return []

        features = self._compute_features(full_df)
        X = features[["log_ratio"]].values
        scores = self.model.decision_function(X)  # higher = more normal
        predictions = self.model.predict(X)  # -1 = anomaly

        features["anomaly_score"] = scores
        features["predicted_anomaly"] = predictions == -1

        cutoff = date.today() - timedelta(days=days_back)
        recent = features[features["purchase_date"].dt.date >= cutoff].copy()

        # Persist anomaly flags to DB
        for _, row in recent.iterrows():
            db.execute(
                Purchase.__table__.update()
                .where(Purchase.id == int(row["id"]))
                .values(
                    is_anomaly=bool(row["predicted_anomaly"]),
                    anomaly_score=float(round(row["anomaly_score"], 4)),
                )
            )
        db.commit()

        results = []
        for _, row in recent[recent["predicted_anomaly"]].iterrows():
            results.append(AnomalyResult(
                purchase_id=int(row["id"]),
                ingredient_name=row["ingredient_name"],
                supplier=row["supplier"],
                purchase_date=row["purchase_date"].date(),
                unit_price=float(row["unit_price"]),
                rolling_avg_price=float(row["rolling_avg"]),
                price_deviation_pct=float(round(row["price_deviation_pct"], 2)),
                anomaly_score=float(round(row["anomaly_score"], 4)),
                is_anomaly=True,
            ))

        return sorted(results, key=lambda r: r.price_deviation_pct, reverse=True)
