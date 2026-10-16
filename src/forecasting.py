"""Forecast baselines, model fitting, and chronological evaluation utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_squared_log_error


def forecast_metrics(actual: pd.Series, predicted: pd.Series) -> dict[str, float]:
    """Return nonnegative-demand forecast metrics."""
    actual_values = np.asarray(actual, dtype=float)
    predicted_values = np.clip(np.asarray(predicted, dtype=float), 0, None)
    return {
        "MAE": float(mean_absolute_error(actual_values, predicted_values)),
        "RMSE": float(mean_squared_error(actual_values, predicted_values) ** 0.5),
        "RMSLE": float(mean_squared_log_error(actual_values, predicted_values) ** 0.5),
    }


def seasonal_naive(history: pd.Series, horizon: int, season_length: int = 7) -> np.ndarray:
    """Repeat the last observed seasonal cycle across the forecast horizon."""
    values = np.asarray(history, dtype=float)
    if len(values) < season_length:
        raise ValueError("History is shorter than the requested season length.")
    season = values[-season_length:]
    return np.resize(season, horizon)
