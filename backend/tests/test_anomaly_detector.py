"""Unit tests for AnomalyDetector — no DB required, uses synthetic data."""
import numpy as np
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from app.ml.anomaly_detector import AnomalyDetector


def _make_purchase_df(n_normal: int = 100, n_anomaly: int = 5) -> pd.DataFrame:
    """Create a synthetic purchase DataFrame with known anomalies."""
    np.random.seed(0)
    base_price = 10.0
    normal_prices = np.random.normal(base_price, 0.3, n_normal)
    anomaly_prices = np.random.uniform(base_price * 1.3, base_price * 1.6, n_anomaly)

    dates = pd.date_range("2025-01-01", periods=n_normal + n_anomaly, freq="D")
    prices = np.concatenate([normal_prices, anomaly_prices])

    return pd.DataFrame({
        "id": range(n_normal + n_anomaly),
        "ingredient_id": 1,
        "purchase_date": dates,
        "unit_price": prices,
        "supplier": "Test Supplier",
        "ingredient_name": "Test Ingredient",
    })


def test_compute_features_adds_log_ratio():
    detector = AnomalyDetector()
    df = _make_purchase_df()
    features = detector._compute_features(df)
    assert "log_ratio" in features.columns
    assert "price_ratio" in features.columns
    assert features["log_ratio"].notna().all()


def test_anomaly_prices_have_higher_log_ratio():
    detector = AnomalyDetector()
    df = _make_purchase_df(n_normal=100, n_anomaly=5)
    features = detector._compute_features(df)
    normal_log_ratio = features.iloc[:100]["log_ratio"].mean()
    anomaly_log_ratio = features.iloc[100:]["log_ratio"].mean()
    assert anomaly_log_ratio > normal_log_ratio, "Anomaly prices should have higher log ratio"


def test_isolation_forest_flags_injected_anomalies():
    """End-to-end: fit on normal data, then score high-priced rows."""
    from sklearn.ensemble import IsolationForest
    import numpy as np

    normal_X = np.random.normal(0, 0.05, (200, 1))
    anomaly_X = np.array([[0.5], [0.6], [0.7]])

    model = IsolationForest(contamination=0.03, random_state=42)
    model.fit(normal_X)

    normal_preds = model.predict(normal_X)
    anomaly_preds = model.predict(anomaly_X)

    # Most normal points should be predicted as inliers (+1)
    assert (normal_preds == 1).mean() > 0.90
    # All injected anomalies should be flagged (-1)
    assert all(p == -1 for p in anomaly_preds)
