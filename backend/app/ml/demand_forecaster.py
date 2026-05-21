"""
Demand forecasting per recipe using XGBoost with temporal features.
Predicts daily quantity sold for the next N days.
"""
from dataclasses import dataclass
from datetime import date, timedelta

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import settings
from app.models.db_models import Sale, Recipe

MODEL_DIR = settings.model_dir


@dataclass
class ForecastPoint:
    forecast_date: date
    predicted_qty: float
    lower_bound: float
    upper_bound: float


@dataclass
class ForecastResult:
    recipe_id: int
    recipe_name: str
    forecast: list[ForecastPoint]
    model_rmse: float


def _make_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["day_of_week"] = df["sale_date"].dt.dayofweek
    df["week_of_year"] = df["sale_date"].dt.isocalendar().week.astype(int)
    df["month"] = df["sale_date"].dt.month
    df["is_weekend"] = (df["day_of_week"] >= 4).astype(int)
    df["lag_1"] = df["quantity_sold"].shift(1).fillna(df["quantity_sold"].mean())
    df["lag_7"] = df["quantity_sold"].shift(7).fillna(df["quantity_sold"].mean())
    df["rolling_7"] = df["quantity_sold"].shift(1).rolling(7, min_periods=1).mean()
    df["rolling_14"] = df["quantity_sold"].shift(1).rolling(14, min_periods=1).mean()
    return df


FEATURE_COLS = ["day_of_week", "week_of_year", "month", "is_weekend", "lag_1", "lag_7", "rolling_7", "rolling_14"]


class DemandForecaster:
    def __init__(self):
        import os
        os.makedirs(MODEL_DIR, exist_ok=True)

    def _model_path(self, recipe_id: int) -> str:
        return f"{MODEL_DIR}/recipe_{recipe_id}.joblib"

    def _load_sales_df(self, db: Session, recipe_id: int) -> pd.DataFrame:
        rows = db.execute(
            select(Sale.sale_date, Sale.quantity_sold)
            .where(Sale.recipe_id == recipe_id)
            .order_by(Sale.sale_date)
        ).fetchall()
        df = pd.DataFrame(rows, columns=["sale_date", "quantity_sold"])
        df["sale_date"] = pd.to_datetime(df["sale_date"])
        return df

    def _train(self, df: pd.DataFrame) -> tuple[xgb.XGBRegressor, float]:
        df = _make_features(df)
        X = df[FEATURE_COLS]
        y = df["quantity_sold"]

        split = int(len(df) * 0.85)
        X_train, X_val = X.iloc[:split], X.iloc[split:]
        y_train, y_val = y.iloc[:split], y.iloc[split:]

        model = xgb.XGBRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=4,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbosity=0,
        )
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

        val_preds = model.predict(X_val)
        rmse = float(np.sqrt(np.mean((val_preds - y_val.values) ** 2)))
        return model, rmse

    def forecast(self, db: Session, recipe_id: int, days: int = 30) -> ForecastResult | None:
        recipe = db.get(Recipe, recipe_id)
        if recipe is None:
            return None

        df = self._load_sales_df(db, recipe_id)
        if len(df) < 14:
            return None

        model_path = self._model_path(recipe_id)
        try:
            model, rmse = joblib.load(model_path)
        except FileNotFoundError:
            model, rmse = self._train(df)
            joblib.dump((model, rmse), model_path)

        # Build future feature rows iteratively
        history_df = _make_features(df.copy())
        last_known_qty = list(df["quantity_sold"].values)

        forecast_points = []
        last_date = df["sale_date"].iloc[-1]

        for i in range(1, days + 1):
            future_date = last_date + timedelta(days=i)

            series = pd.Series(last_known_qty)
            lag_1 = float(series.iloc[-1])
            lag_7 = float(series.iloc[-7]) if len(series) >= 7 else float(series.mean())
            rolling_7 = float(series.iloc[-7:].mean())
            rolling_14 = float(series.iloc[-14:].mean())

            row = pd.DataFrame([{
                "day_of_week": future_date.weekday(),
                "week_of_year": future_date.isocalendar().week,
                "month": future_date.month,
                "is_weekend": int(future_date.weekday() >= 4),
                "lag_1": lag_1,
                "lag_7": lag_7,
                "rolling_7": rolling_7,
                "rolling_14": rolling_14,
            }])

            pred = float(model.predict(row[FEATURE_COLS])[0])
            pred = max(0, round(pred, 1))

            # Confidence interval based on validation RMSE
            lower = max(0, round(pred - 1.96 * rmse, 1))
            upper = round(pred + 1.96 * rmse, 1)

            forecast_points.append(ForecastPoint(
                forecast_date=future_date.date(),
                predicted_qty=pred,
                lower_bound=lower,
                upper_bound=upper,
            ))
            last_known_qty.append(pred)

        return ForecastResult(
            recipe_id=recipe_id,
            recipe_name=recipe.name,
            forecast=forecast_points,
            model_rmse=round(rmse, 2),
        )
