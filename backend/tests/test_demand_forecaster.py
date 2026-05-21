"""Unit tests for DemandForecaster feature engineering — no DB or model required."""
import pandas as pd
import numpy as np
import pytest
from datetime import date, timedelta

from app.ml.demand_forecaster import _make_features, FEATURE_COLS


def _make_sales_df(n_days: int = 30) -> pd.DataFrame:
    dates = pd.date_range(date.today() - timedelta(days=n_days), periods=n_days, freq="D")
    np.random.seed(0)
    qty = np.random.randint(10, 30, size=n_days).astype(float)
    return pd.DataFrame({"sale_date": dates, "quantity_sold": qty})


def test_make_features_columns_present():
    df = _make_sales_df(30)
    features = _make_features(df)
    for col in FEATURE_COLS:
        assert col in features.columns, f"Missing feature column: {col}"


def test_weekend_flag_correct():
    df = _make_sales_df(14)
    features = _make_features(df)
    for _, row in features.iterrows():
        expected = 1 if row["sale_date"].dayofweek >= 4 else 0
        assert row["is_weekend"] == expected


def test_lag_1_is_previous_day():
    df = _make_sales_df(10)
    features = _make_features(df)
    # lag_1 at index i should equal quantity_sold at index i-1
    for i in range(1, len(features)):
        assert features["lag_1"].iloc[i] == features["quantity_sold"].iloc[i - 1]


def test_rolling_7_no_negative():
    df = _make_sales_df(30)
    features = _make_features(df)
    assert (features["rolling_7"] >= 0).all()
    assert (features["rolling_14"] >= 0).all()


def test_feature_count():
    df = _make_sales_df(30)
    features = _make_features(df)
    assert len(features.columns) >= len(FEATURE_COLS) + 2  # original cols + all features
