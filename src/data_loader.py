"""Safe, reusable loading and profiling utilities for competition CSV files."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


EXPECTED_FILES = (
    "train.csv",
    "test.csv",
    "stores.csv",
    "transactions.csv",
    "holidays_events.csv",
    "oil.csv",
    "sample_submission.csv",
)

DATE_FILES = {
    "train.csv",
    "test.csv",
    "transactions.csv",
    "holidays_events.csv",
    "oil.csv",
}

DATASET_DESCRIPTIONS = {
    "train.csv": "Historical daily sales at date-store-product-family grain.",
    "test.csv": "Competition forecast horizon at date-store-product-family grain.",
    "stores.csv": "Store location, type, and cluster attributes.",
    "transactions.csv": "Observed daily transaction counts by store.",
    "holidays_events.csv": "Holiday and event records at national, regional, or local scope.",
    "oil.csv": "Daily WTI oil-price observations supplied by the competition.",
    "sample_submission.csv": "Required Kaggle prediction-output structure.",
}

CANDIDATE_KEYS = {
    "train.csv": ["id"],
    "test.csv": ["id"],
    "stores.csv": ["store_nbr"],
    "transactions.csv": ["date", "store_nbr"],
    "holidays_events.csv": [
        "date", "type", "locale", "locale_name", "description", "transferred"
    ],
    "oil.csv": ["date"],
    "sample_submission.csv": ["id"],
}


def find_project_root(start: Path | None = None) -> Path:
    """Return the nearest parent containing both `data` and `notebooks`."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "data").is_dir() and (candidate / "notebooks").is_dir():
            return candidate
    raise FileNotFoundError(
        "Project root not found. Start Python inside this repository or a subfolder."
    )


def inspect_available_files(
    raw_data_dir: Path, expected_files: Iterable[str] = EXPECTED_FILES
) -> pd.DataFrame:
    """Return existence and file-size metadata for expected raw inputs."""
    rows = []
    for filename in expected_files:
        path = raw_data_dir / filename
        rows.append(
            {
                "file": filename,
                "available": path.is_file(),
                "size_mb": round(path.stat().st_size / 1024**2, 3) if path.is_file() else None,
            }
        )
    return pd.DataFrame(rows)


def load_dataset(raw_data_dir: Path, filename: str) -> pd.DataFrame:
    """Load one known CSV and parse its date column when applicable."""
    if filename not in EXPECTED_FILES:
        raise ValueError(f"Unexpected dataset name: {filename}")

    path = raw_data_dir / filename
    if not path.is_file():
        raise FileNotFoundError(
            f"Required input not found: {path}. See data/README.md for setup instructions."
        )

    parse_dates = ["date"] if filename in DATE_FILES else None
    return pd.read_csv(path, parse_dates=parse_dates, low_memory=False)


def load_all_available(raw_data_dir: Path) -> dict[str, pd.DataFrame]:
    """Load every expected CSV that is present, leaving missing files explicit."""
    inventory = inspect_available_files(raw_data_dir)
    return {
        filename: load_dataset(raw_data_dir, filename)
        for filename in inventory.loc[inventory["available"], "file"]
    }


def profile_dataset(filename: str, frame: pd.DataFrame) -> dict[str, object]:
    """Build a compact structural and quality profile for one dataset."""
    return {
        "file": filename,
        "rows": len(frame),
        "columns": frame.shape[1],
        "memory_mb": round(frame.memory_usage(deep=True).sum() / 1024**2, 2),
        "exact_duplicate_rows": int(frame.duplicated().sum()),
        "missing_cells": int(frame.isna().sum().sum()),
        "date_min": frame["date"].min() if "date" in frame else pd.NaT,
        "date_max": frame["date"].max() if "date" in frame else pd.NaT,
    }
