"""Reusable utilities for the grocery retail demand project.

This package provides modular tools for end-to-end retail demand forecasting:
    - data_loader: File verification, safe CSV loading, and dataset profiling.
    - preprocessing: Calendar feature extraction, holiday mapping, oil data alignment,
      and unified analysis panel assembly.
    - features: Leakage-safe time-series lags and rolling statistics.
    - forecasting: Evaluative metrics (MAE, RMSE, RMSLE) and baseline models (Seasonal Naive).
    - visualization: Consistent plotting styles and high-resolution figure export helpers.
    - eda: Advanced exploratory demand classification (Croston/Syntetos-Boylan), Quincena
      payday dynamics, earthquake shock assessment, category co-movement correlations,
      and promotional elasticity profiling.
"""

from __future__ import annotations

__all__ = [
    "data_loader",
    "eda",
    "features",
    "forecasting",
    "preprocessing",
    "visualization",
]
