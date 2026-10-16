"""Safe, reusable loading and profiling utilities for competition CSV files.

This module provides utility functions to locate the project root directory,
verify and inspect expected raw data files, load them with consistent date
parsing, and generate summary data-quality profiles.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


# ---------------------------------------------------------------------------
# Constants and Metadata Definitions
# ---------------------------------------------------------------------------

# The complete set of expected raw CSV filenames from the Kaggle Store Sales competition.
EXPECTED_FILES = (
    "train.csv",
    "test.csv",
    "stores.csv",
    "transactions.csv",
    "holidays_events.csv",
    "oil.csv",
    "sample_submission.csv",
)

# Subset of raw files containing temporal 'date' columns requiring datetime conversion.
DATE_FILES = {
    "train.csv",
    "test.csv",
    "transactions.csv",
    "holidays_events.csv",
    "oil.csv",
}

# Human-readable business descriptions explaining the context and grain of each file.
DATASET_DESCRIPTIONS = {
    "train.csv": "Historical daily sales at date-store-product-family grain.",
    "test.csv": "Competition forecast horizon at date-store-product-family grain.",
    "stores.csv": "Store location, type, and cluster attributes.",
    "transactions.csv": "Observed daily transaction counts by store.",
    "holidays_events.csv": "Holiday and event records at national, regional, or local scope.",
    "oil.csv": "Daily WTI oil-price observations supplied by the competition.",
    "sample_submission.csv": "Required Kaggle prediction-output structure.",
}

# The expected primary or composite key attributes that uniquely identify records in each table.
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


# ---------------------------------------------------------------------------
# File System & Loading Utilities
# ---------------------------------------------------------------------------

def find_project_root(start: Path | None = None) -> Path:
    """Return the nearest parent containing both `data` and `notebooks`.

    This allows scripts and notebooks to reliably locate project directories
    regardless of whether Python was launched from the repository root,
    the notebooks directory, or a nested subdirectory.

    Args:
        start: Optional starting path for resolution. Defaults to current working directory.

    Returns:
        Path: The absolute path to the repository root directory.

    Raises:
        FileNotFoundError: If neither the current directory nor any of its parents
            contains both 'data' and 'notebooks' folders.
    """
    current = (start or Path.cwd()).resolve()
    # Traverse upwards through parent directories until the root markers are found
    for candidate in (current, *current.parents):
        if (candidate / "data").is_dir() and (candidate / "notebooks").is_dir():
            return candidate
    raise FileNotFoundError(
        "Project root not found. Start Python inside this repository or a subfolder."
    )


def inspect_available_files(
    raw_data_dir: Path, expected_files: Iterable[str] = EXPECTED_FILES
) -> pd.DataFrame:
    """Return existence and file-size metadata for expected raw inputs.

    Checks each expected raw file against disk, recording availability and
    size in megabytes for audit and environment validation.

    Args:
        raw_data_dir: Directory path containing the raw competition files.
        expected_files: Iterable of expected filenames to check. Defaults to EXPECTED_FILES.

    Returns:
        pd.DataFrame: Summary table with columns ['file', 'available', 'size_mb'].
    """
    rows = []
    for filename in expected_files:
        path = raw_data_dir / filename
        is_file = path.is_file()
        # Convert file size from bytes to megabytes (MB) rounded to 3 decimal places
        size_mb = round(path.stat().st_size / 1024**2, 3) if is_file else None
        rows.append(
            {
                "file": filename,
                "available": is_file,
                "size_mb": size_mb,
            }
        )
    return pd.DataFrame(rows)


def load_dataset(raw_data_dir: Path, filename: str) -> pd.DataFrame:
    """Load one known CSV and parse its date column when applicable.

    Enforces a strict filename whitelist and ensures automatic conversion
    of date strings into datetime objects for temporal consistency across notebooks.

    Args:
        raw_data_dir: Directory path containing the raw data files.
        filename: Name of the CSV file to load (must be in EXPECTED_FILES).

    Returns:
        pd.DataFrame: The loaded DataFrame with parsed dates if applicable.

    Raises:
        ValueError: If filename is not in EXPECTED_FILES.
        FileNotFoundError: If the file does not exist on disk.
    """
    # Restrict filenames to the documented competition inputs. This prevents a
    # similarly named CSV from another Downloads project being used by mistake.
    if filename not in EXPECTED_FILES:
        raise ValueError(f"Unexpected dataset name: {filename}")

    path = raw_data_dir / filename
    if not path.is_file():
        raise FileNotFoundError(
            f"Required input not found: {path}. See data/README.md for setup instructions."
        )

    # Parse dates at ingestion so every downstream notebook uses one consistent data type.
    parse_dates = ["date"] if filename in DATE_FILES else None
    return pd.read_csv(path, parse_dates=parse_dates, low_memory=False)


def load_all_available(raw_data_dir: Path) -> dict[str, pd.DataFrame]:
    """Load every expected CSV that is present, leaving missing files explicit.

    Scans the raw data folder and reads all available expected CSVs into a dictionary.

    Args:
        raw_data_dir: Directory path containing raw CSV files.

    Returns:
        dict[str, pd.DataFrame]: Mapping of filenames to their loaded DataFrames.
    """
    inventory = inspect_available_files(raw_data_dir)
    # Only load files confirmed to exist on disk
    return {
        filename: load_dataset(raw_data_dir, filename)
        for filename in inventory.loc[inventory["available"], "file"]
    }


def profile_dataset(filename: str, frame: pd.DataFrame) -> dict[str, object]:
    """Build a compact structural and quality profile for one dataset.

    Computes basic dimensionality, memory footprint, duplicate rows, missing
    cell counts, and temporal boundaries (min/max dates if present).

    Args:
        filename: The name or identifier of the dataset.
        frame: The pandas DataFrame to profile.

    Returns:
        dict[str, object]: Dictionary containing profiling statistics:
            - 'file': Dataset filename
            - 'rows': Total row count
            - 'columns': Total column count
            - 'memory_mb': Deep memory consumption in MB
            - 'exact_duplicate_rows': Count of duplicated rows across all columns
            - 'missing_cells': Total count of NaN/null values across all columns
            - 'date_min': Earliest date in the dataset (or NaT if no date column)
            - 'date_max': Latest date in the dataset (or NaT if no date column)
    """
    return {
        "file": filename,
        "rows": len(frame),
        "columns": frame.shape[1],
        # Deep inspection accounts for object/string memory, not just fixed-size buffers
        "memory_mb": round(frame.memory_usage(deep=True).sum() / 1024**2, 2),
        "exact_duplicate_rows": int(frame.duplicated().sum()),
        "missing_cells": int(frame.isna().sum().sum()),
        "date_min": frame["date"].min() if "date" in frame else pd.NaT,
        "date_max": frame["date"].max() if "date" in frame else pd.NaT,
    }
