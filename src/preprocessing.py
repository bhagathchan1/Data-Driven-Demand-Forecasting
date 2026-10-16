"""Cleaning and dataset-integration functions.

This module provides data transformations to construct a unified retail panel:
    - Calendar feature extraction with memory-efficient integer datatypes.
    - Daily oil series preparation with explicit gap filling and audit tracking.
    - Multi-tiered holiday mapping matching national, regional, and local events to stores.
    - Validated panel merging to combine sales, store attributes, foot traffic, oil,
      and promotion intensity while guarding against grain explosion.
    - Systematic selection of representative stores and product families for deep-dive
      operational forecasting.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Calendar & Temporal Feature Engineering
# ---------------------------------------------------------------------------

def add_date_features(frame: pd.DataFrame, date_column: str = "date") -> pd.DataFrame:
    """Add calendar fields without modifying the input frame.

    Extracts cyclical calendar dimensions (year, month, quarter, ISO week,
    day-of-week, day-of-month, and weekend indicator) using downcasted integer
    types to minimize memory footprint on large datasets.

    Args:
        frame: Input DataFrame containing a date column.
        date_column: Name of the date column. Defaults to "date".

    Returns:
        pd.DataFrame: A copy of the DataFrame with added calendar feature columns:
            - 'year' (int16): 4-digit calendar year
            - 'month' (int8): Month of the year (1-12)
            - 'quarter' (int8): Calendar quarter (1-4)
            - 'week' (int16): ISO calendar week number (1-53)
            - 'day_of_week' (int8): Day of week (0=Monday, 6=Sunday)
            - 'day_of_month' (int8): Day of month (1-31)
            - 'is_weekend' (bool): True if day_of_week is Saturday or Sunday
    """
    result = frame.copy()
    dates = pd.to_datetime(result[date_column], errors="raise")
    iso_calendar = dates.dt.isocalendar()

    # Downcast numeric types to compact signed integers to reduce RAM usage
    result["year"] = dates.dt.year.astype("int16")
    result["month"] = dates.dt.month.astype("int8")
    result["quarter"] = dates.dt.quarter.astype("int8")
    result["week"] = iso_calendar.week.astype("int16")
    result["day_of_week"] = dates.dt.dayofweek.astype("int8")
    result["day_of_month"] = dates.dt.day.astype("int8")
    # Saturday (5) and Sunday (6) define retail weekend patterns
    result["is_weekend"] = dates.dt.dayofweek.ge(5)
    return result


# ---------------------------------------------------------------------------
# External Data Preparation (Oil & Holidays)
# ---------------------------------------------------------------------------

def prepare_daily_oil(oil: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Create a daily oil series and flag values filled from prior observations.

    Crude oil prices (WTI) are only published on business trading days, whereas
    grocery store sales operate every day of the week. This function generates
    a continuous daily date range, left-joins published prices, creates an explicit
    audit indicator for filled days, and forward-fills (then back-fills) missing values.

    Args:
        oil: DataFrame containing raw oil price records with ['date', 'dcoilwtico'].
        start: Starting timestamp for the daily calendar range.
        end: Ending timestamp for the daily calendar range.

    Returns:
        pd.DataFrame: Daily calendar DataFrame with ['date', 'dcoilwtico', 'oil_value_missing'].
    """
    # Oil is reported on business days, but sales are analyzed on a daily calendar.
    clean = oil.copy().sort_values("date").drop_duplicates("date")
    calendar = pd.DataFrame({"date": pd.date_range(start, end, freq="D")})
    daily = calendar.merge(clean, on="date", how="left", validate="one_to_one")

    # Preserve an audit flag before carrying the latest known value through gaps.
    # This allows analysts to distinguish true market observations from carried-forward prices.
    daily["oil_value_missing"] = daily["dcoilwtico"].isna()
    # Forward-fill carries Friday's price through Saturday/Sunday; backfill handles leading dates
    daily["dcoilwtico"] = daily["dcoilwtico"].ffill().bfill()
    return daily


def build_store_holiday_features(
    holidays: pd.DataFrame, stores: pd.DataFrame, dates: pd.Series
) -> pd.DataFrame:
    """Map observed holidays to stores using national, regional, and local scope.

    A holiday in Ecuador can be National (affects all stores), Regional (affects stores
    in a specific state/province), or Local (affects stores in a specific city).
    Transferred holidays are celebrated on an alternate date and must not be flagged
    on their original calendar date.

    Args:
        holidays: DataFrame of holiday events with ['date', 'type', 'locale', 'locale_name', 'transferred'].
        stores: Store master DataFrame with ['store_nbr', 'city', 'state'].
        dates: Series of unique dates appearing in the sales panel.

    Returns:
        pd.DataFrame: Store-date holiday table with columns:
            - 'date': Date of observation
            - 'store_nbr': Store identifier
            - 'is_national_holiday': True if national event occurred on date
            - 'is_regional_holiday': True if regional event matched store's state
            - 'is_local_holiday': True if local event matched store's city
            - 'is_holiday': True if any of the above holiday types apply
            - 'holiday_scope_count': Count of applicable holiday scopes (0 to 3)
    """
    # A transferred record is not observed on its original calendar date.
    observed = holidays.loc[~holidays["transferred"]].copy()

    # Form a Cartesian product of all unique panel dates and stores
    relevant_dates = pd.DataFrame({"date": pd.Series(dates.unique())})
    grid = relevant_dates.assign(_key=1).merge(
        stores[["store_nbr", "city", "state"]].assign(_key=1), on="_key"
    ).drop(columns="_key")

    # Group events by their stated geographic scope to prevent cross-scope duplication
    national_dates = set(observed.loc[observed["locale"].eq("National"), "date"])
    regional = observed.loc[observed["locale"].eq("Regional"), ["date", "locale_name"]]
    local = observed.loc[observed["locale"].eq("Local"), ["date", "locale_name"]]

    # Match national holidays globally across all stores
    grid["is_national_holiday"] = grid["date"].isin(national_dates)

    # Match regional holidays against the store's state (locale_name corresponds to state)
    regional_keys = set(map(tuple, regional.to_numpy()))
    # Match local holidays against the store's city (locale_name corresponds to city)
    local_keys = set(map(tuple, local.to_numpy()))

    grid["is_regional_holiday"] = [
        (date, state) in regional_keys for date, state in zip(grid["date"], grid["state"])
    ]
    grid["is_local_holiday"] = [
        (date, city) in local_keys for date, city in zip(grid["date"], grid["city"])
    ]

    holiday_columns = [
        "is_national_holiday", "is_regional_holiday", "is_local_holiday"
    ]
    # Consolidate overall holiday indicator and count of overlapping holiday scopes
    grid["is_holiday"] = grid[holiday_columns].any(axis=1)
    grid["holiday_scope_count"] = grid[holiday_columns].sum(axis=1).astype("int8")

    return grid[["date", "store_nbr", *holiday_columns, "is_holiday", "holiday_scope_count"]]


# ---------------------------------------------------------------------------
# Master Analysis Panel Construction
# ---------------------------------------------------------------------------

def build_analysis_panel(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Create a validated full-grain panel while retaining missingness indicators.

    Integrates sales history with store metadata, daily foot traffic (transactions),
    aligned oil prices, geographic holiday features, and extracted calendar attributes.
    Enforces strict grain and row count assertions to prevent duplicate sales or
    unintended drops.

    Args:
        datasets: Dictionary mapping filenames to loaded DataFrames:
            - 'train.csv': Historical daily sales
            - 'stores.csv': Store metadata
            - 'transactions.csv': Daily store transaction counts
            - 'oil.csv': Daily oil prices
            - 'holidays_events.csv': Holiday calendar

    Returns:
        pd.DataFrame: Fully integrated analysis panel at date x store x family grain.

    Raises:
        ValueError: If store metadata does not match all sales stores,
            if any merge changes row count from original train data,
            or if the final table contains duplicate date-store-family rows.
    """
    train = datasets["train.csv"].copy()
    stores = datasets["stores.csv"].copy()
    transactions = datasets["transactions.csv"].copy()
    oil = datasets["oil.csv"].copy()
    holidays = datasets["holidays_events.csv"].copy()

    # Optimize data types to category and downcasted integers to reduce RAM consumption
    train["family"] = train["family"].astype("category")
    train["store_nbr"] = pd.to_numeric(train["store_nbr"], downcast="integer")
    train["onpromotion"] = pd.to_numeric(train["onpromotion"], downcast="integer")

    for column in ("city", "state", "type"):
        stores[column] = stores[column].astype("category")
    stores["store_nbr"] = pd.to_numeric(stores["store_nbr"], downcast="integer")
    stores["cluster"] = pd.to_numeric(stores["cluster"], downcast="integer")
    transactions["store_nbr"] = pd.to_numeric(
        transactions["store_nbr"], downcast="integer"
    )

    # The store master must add attributes without changing the sales-table grain.
    # Using validate="many_to_one" ensures store_nbr in stores is unique.
    panel = train.merge(stores, on="store_nbr", how="left", validate="many_to_one")
    if panel[["city", "state", "type", "cluster"]].isna().any().any():
        raise ValueError("Store join left unmatched sales rows.")

    # A left join keeps every sales observation; missing traffic remains explicit.
    # Note: Closed stores or unrecorded transaction days produce NaN in transactions.
    panel = panel.merge(
        transactions, on=["date", "store_nbr"], how="left", validate="many_to_one"
    )
    panel["transaction_record_missing"] = panel["transactions"].isna()

    # Oil is converted to a daily series before joining to avoid weekend gaps.
    daily_oil = prepare_daily_oil(oil, panel["date"].min(), panel["date"].max())
    panel = panel.merge(daily_oil, on="date", how="left", validate="many_to_one")

    # Holiday scope is resolved before the join to prevent same-date row multiplication.
    holiday_features = build_store_holiday_features(holidays, stores, panel["date"])
    panel = panel.merge(
        holiday_features, on=["date", "store_nbr"], how="left", validate="many_to_one"
    )

    # Append calendar features (day of week, month, etc.)
    panel = add_date_features(panel)

    # Log1p transformation stabilizes promotional item counts for operational modeling
    panel["promotion_intensity"] = np.log1p(panel["onpromotion"])

    # These assertions turn silent join errors into visible failures.
    if len(panel) != len(train):
        raise ValueError("A merge changed the sales-panel row count.")
    if panel.duplicated(["date", "store_nbr", "family"]).any():
        raise ValueError("The prepared panel is not unique at its intended grain.")

    return panel


# ---------------------------------------------------------------------------
# Scope & Cohort Selection
# ---------------------------------------------------------------------------

def choose_analysis_scope(panel: pd.DataFrame) -> tuple[list[int], list[str], pd.Timestamp]:
    """Select well-covered representative stores, important families, and 24 months.

    For detailed exploratory and forecasting deep-dives, analyzing all 54 stores x
    33 families x 1,700 dates is redundant and computationally heavy. This function
    selects a balanced portfolio of 5 stores and 5 product families that captures:
        - Scale diversity (highest volume, median volume, lowest volume)
        - Volatility diversity (highest coefficient of variation)
        - High data reliability (minimum 90% transaction coverage and active sales days)
        - A 24-month historical analysis window ending at the latest available date.

    Args:
        panel: Fully assembled analysis panel DataFrame.

    Returns:
        tuple[list[int], list[str], pd.Timestamp]:
            - selected_stores: List of 5 chosen store numbers
            - selected_families: List of 5 chosen product family names
            - start_date: Starting timestamp for the 24-month evaluation window

    Raises:
        ValueError: If fewer than 5 stores meet the 90% data coverage requirements.
    """
    # Aggregate sales and transactions to store-day grain
    store_daily = panel.groupby(["store_nbr", "date"], as_index=False).agg(
        sales=("sales", "sum"), transactions=("transactions", "max")
    )
    # Calculate volume and coverage statistics per store
    store_metrics = store_daily.groupby("store_nbr").agg(
        sum=("sales", "sum"), mean=("sales", "mean"), std=("sales", "std"),
        transaction_coverage_pct=("transactions", lambda values: 100 * values.notna().mean()),
        active_sales_days_pct=("sales", lambda values: 100 * values.gt(0).mean()),
    )
    # Coefficient of Variation (CV) = std / mean (measures relative demand volatility)
    store_metrics["cv"] = store_metrics["std"] / store_metrics["mean"]

    # Exclude later-opening or poorly covered stores from ordinary CV comparisons.
    eligible = store_metrics.loc[
        store_metrics["transaction_coverage_pct"].ge(90)
        & store_metrics["active_sales_days_pct"].ge(90)
    ]
    if len(eligible) < 5:
        raise ValueError("Fewer than five stores meet the 90% coverage rule.")

    # Represent scale and uncertainty instead of selecting only the largest stores.
    ranked = eligible.sort_values("sum", ascending=False)
    # 1 & 2: Top two highest-volume stores (commercial flagships)
    selections = [int(ranked.index[0]), int(ranked.index[1])]
    # 3: Median-volume store (typical representative operation)
    median_target = eligible["sum"].median()
    selections.append(int((eligible["sum"] - median_target).abs().idxmin()))
    # 4: Lowest-volume eligible store (small format or quiet location)
    selections.append(int(eligible["sum"].idxmin()))
    # 5: Most volatile eligible store (highest CV among remaining stores)
    selections.append(int(eligible.loc[~eligible.index.isin(selections), "cv"].idxmax()))
    selected_stores = list(dict.fromkeys(selections))[:5]

    # Families combine commercial importance with one deliberately volatile case.
    family_daily = panel.groupby(["family", "date"], as_index=False)["sales"].sum()
    family_metrics = family_daily.groupby("family")["sales"].agg(["sum", "mean", "std"])
    family_metrics["cv"] = family_metrics["std"] / family_metrics["mean"]

    # Select top 4 product families by total revenue volume (e.g. Grocery, Beverages, Produce, etc.)
    selected_families = list(family_metrics.nlargest(4, "sum").index)
    # Select the most volatile family within the top 15 volume categories
    top_volume_pool = family_metrics.nlargest(15, "sum")
    volatility_choice = top_volume_pool.loc[
        ~top_volume_pool.index.isin(selected_families), "cv"
    ].idxmax()
    selected_families.append(str(volatility_choice))

    # Define a clean 24-month horizon ending at panel's max date
    start_date = panel["date"].max() - pd.DateOffset(months=24) + pd.Timedelta(days=1)
    return selected_stores, selected_families, pd.Timestamp(start_date)
