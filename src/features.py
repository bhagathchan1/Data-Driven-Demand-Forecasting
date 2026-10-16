"""Time-series and operational feature engineering.

This module provides feature engineering routines for retail demand time-series.
All lag and rolling aggregate calculations strictly enforce chronological separation
to prevent data leakage (lookahead bias) when evaluating forecasting models.
"""

from __future__ import annotations

import pandas as pd


def add_lag_features(series_frame: pd.DataFrame) -> pd.DataFrame:
    """Create leakage-safe lags and rolling features within each demand series.

    For each individual demand series (identified by store_nbr and product family),
    this function computes:
        - Lag 1: Prior day's sales (captures immediate daily momentum / day-after effects).
        - Lag 7: Same day last week (captures day-of-week weekly seasonality).
        - Lag 14: Same day two weeks ago (captures bi-weekly pay-cycle or order cycles).
        - Lag 28: Same day four weeks ago (captures monthly baseline demand).
        - Rolling Mean 7: 7-day trailing average (shifted by 1 to exclude current day).
        - Rolling Mean 28: 28-day trailing average (shifted by 1 to exclude current day).

    Data leakage is prevented by:
        1. Explicitly sorting chronologically by [store_nbr, family, date].
        2. Grouping strictly within each store and family combination.
        3. Shifting series by 1 period before computing rolling window metrics so
           that today's target value is never included in the rolling summary.

    Args:
        series_frame: DataFrame containing ['date', 'store_nbr', 'family', 'sales'].

    Returns:
        pd.DataFrame: A sorted copy of the DataFrame with added feature columns:
            - 'lag_1', 'lag_7', 'lag_14', 'lag_28'
            - 'rolling_mean_7', 'rolling_mean_28'
    """
    # Sorting ensures each shift operation strictly retrieves genuine prior observations
    result = series_frame.sort_values(["store_nbr", "family", "date"]).copy()

    # Group sales by individual store and family time-series
    groups = result.groupby(["store_nbr", "family"], sort=False)["sales"]

    # Generate fixed calendar lags:
    # 1 (yesterday), 7 (1 week ago), 14 (2 weeks ago), 28 (4 weeks ago)
    for lag in (1, 7, 14, 28):
        result[f"lag_{lag}"] = groups.shift(lag)

    # Shift by 1 first so rolling statistics reflect only strictly completed past days;
    # today's sales can never leak into the feature set used to predict today's demand.
    shifted = groups.shift(1)
    series_keys = [result["store_nbr"], result["family"]]

    # 7-day rolling window: captures short-term trailing volume pace
    result["rolling_mean_7"] = shifted.groupby(series_keys).transform(
        lambda values: values.rolling(7).mean()
    )

    # 28-day rolling window: captures broader monthly baseline run-rate
    result["rolling_mean_28"] = shifted.groupby(series_keys).transform(
        lambda values: values.rolling(28).mean()
    )

    return result
