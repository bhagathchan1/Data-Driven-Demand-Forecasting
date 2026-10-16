"""Forecast baselines, model fitting, and chronological evaluation utilities.

This module provides tools for:
    - Computing demand forecasting evaluation metrics: Mean Absolute Error (MAE),
      Root Mean Squared Error (RMSE), and Root Mean Squared Log Error (RMSLE).
    - Post-processing forecasts to guarantee non-negativity (retail demand cannot be negative).
    - Implementing a Seasonal Naive baseline benchmark representing standard weekly cycles.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_squared_log_error


def forecast_metrics(actual: pd.Series, predicted: pd.Series) -> dict[str, float]:
    """Return nonnegative-demand forecast metrics.

    Calculates three standard retail forecasting performance metrics:
        1. MAE (Mean Absolute Error):
           Measures the average magnitude of errors in raw unit terms. Intuitive for
           inventory and replenishment planning.
        2. RMSE (Root Mean Squared Error):
           Penalizes large forecast errors more severely than small ones, highlighting
           severe stockout or overstock risks.
        3. RMSLE (Root Mean Squared Logarithmic Error):
           Measures percentage/relative errors and prevents high-volume categories
           from dominating model evaluation. This is the primary Kaggle competition metric.

    Note:
        Predictions are clipped at zero before evaluation because negative sales
        forecasts have no physical operational meaning in retail inventory management.

    Args:
        actual: Series or array-like of observed actual demand values.
        predicted: Series or array-like of model-predicted demand values.

    Returns:
        dict[str, float]: Dictionary containing:
            - 'MAE': Mean Absolute Error
            - 'RMSE': Root Mean Squared Error
            - 'RMSLE': Root Mean Squared Log Error
    """
    actual_values = np.asarray(actual, dtype=float)

    # Negative forecasts have no direct operational meaning for grocery sales;
    # clipping at 0 ensures physically valid predictions and avoids math domain errors in log
    predicted_values = np.clip(np.asarray(predicted, dtype=float), 0, None)

    return {
        "MAE": float(mean_absolute_error(actual_values, predicted_values)),
        "RMSE": float(mean_squared_error(actual_values, predicted_values) ** 0.5),
        "RMSLE": float(mean_squared_log_error(actual_values, predicted_values) ** 0.5),
    }


def seasonal_naive(history: pd.Series, horizon: int, season_length: int = 7) -> np.ndarray:
    """Repeat the last observed seasonal cycle across the forecast horizon.

    The Seasonal Naive benchmark assumes that demand in the forecast period will
    exactly replicate the values observed during the most recent completed seasonal cycle
    (e.g., this coming Tuesday will match last Tuesday). In retail forecasting, this is
    a strong baseline that machine learning models must beat to justify adoption.

    Args:
        history: Historical sales observations ordered chronologically.
        horizon: Number of periods (days) to forecast into the future.
        season_length: Length of the seasonal cycle in days. Defaults to 7 (weekly pattern).

    Returns:
        np.ndarray: Array of forecast values of length `horizon`.

    Raises:
        ValueError: If historical observations are fewer than `season_length`.
    """
    values = np.asarray(history, dtype=float)
    if len(values) < season_length:
        raise ValueError("History is shorter than the requested season length.")

    # Extract the most recent complete seasonal cycle (e.g., the last 7 days)
    season = values[-season_length:]

    # Repeat (tile) the seasonal slice across the forecast horizon
    return np.resize(season, horizon)
