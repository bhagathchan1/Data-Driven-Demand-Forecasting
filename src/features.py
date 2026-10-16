"""Time-series and operational feature engineering."""

from __future__ import annotations

import pandas as pd


def add_lag_features(series_frame: pd.DataFrame) -> pd.DataFrame:
    """Create leakage-safe lags and rolling features within each demand series."""
    # Sorting makes each shift represent a genuine earlier observation.
    result = series_frame.sort_values(["store_nbr", "family", "date"]).copy()
    groups = result.groupby(["store_nbr", "family"], sort=False)["sales"]
    for lag in (1, 7, 14, 28):
        result[f"lag_{lag}"] = groups.shift(lag)

    # Shift before rolling so today's sales can never help predict itself.
    shifted = groups.shift(1)
    result["rolling_mean_7"] = shifted.groupby(
        [result["store_nbr"], result["family"]]
    ).transform(lambda values: values.rolling(7).mean())
    result["rolling_mean_28"] = shifted.groupby(
        [result["store_nbr"], result["family"]]
    ).transform(lambda values: values.rolling(28).mean())
    return result
