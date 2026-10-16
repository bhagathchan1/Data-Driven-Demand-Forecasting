"""Cleaning and dataset-integration functions."""

from __future__ import annotations

import numpy as np
import pandas as pd


def add_date_features(frame: pd.DataFrame, date_column: str = "date") -> pd.DataFrame:
    """Add calendar fields without modifying the input frame."""
    result = frame.copy()
    dates = pd.to_datetime(result[date_column], errors="raise")
    iso_calendar = dates.dt.isocalendar()
    result["year"] = dates.dt.year.astype("int16")
    result["month"] = dates.dt.month.astype("int8")
    result["quarter"] = dates.dt.quarter.astype("int8")
    result["week"] = iso_calendar.week.astype("int16")
    result["day_of_week"] = dates.dt.dayofweek.astype("int8")
    result["day_of_month"] = dates.dt.day.astype("int8")
    result["is_weekend"] = dates.dt.dayofweek.ge(5)
    return result


def prepare_daily_oil(oil: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """Create a daily oil series and flag values filled from prior observations."""
    # Oil is reported on business days, but sales are analyzed on a daily calendar.
    clean = oil.copy().sort_values("date").drop_duplicates("date")
    calendar = pd.DataFrame({"date": pd.date_range(start, end, freq="D")})
    daily = calendar.merge(clean, on="date", how="left", validate="one_to_one")

    # Preserve an audit flag before carrying the latest known value through gaps.
    daily["oil_value_missing"] = daily["dcoilwtico"].isna()
    daily["dcoilwtico"] = daily["dcoilwtico"].ffill().bfill()
    return daily


def build_store_holiday_features(
    holidays: pd.DataFrame, stores: pd.DataFrame, dates: pd.Series
) -> pd.DataFrame:
    """Map observed holidays to stores using national, regional, and local scope."""
    # A transferred record is not observed on its original calendar date.
    observed = holidays.loc[~holidays["transferred"]].copy()
    relevant_dates = pd.DataFrame({"date": pd.Series(dates.unique())})
    grid = relevant_dates.assign(_key=1).merge(
        stores[["store_nbr", "city", "state"]].assign(_key=1), on="_key"
    ).drop(columns="_key")

    # Apply each event only to stores inside its stated geographic scope.
    national_dates = set(observed.loc[observed["locale"].eq("National"), "date"])
    regional = observed.loc[observed["locale"].eq("Regional"), ["date", "locale_name"]]
    local = observed.loc[observed["locale"].eq("Local"), ["date", "locale_name"]]

    grid["is_national_holiday"] = grid["date"].isin(national_dates)
    regional_keys = set(map(tuple, regional.to_numpy()))
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
    grid["is_holiday"] = grid[holiday_columns].any(axis=1)
    grid["holiday_scope_count"] = grid[holiday_columns].sum(axis=1).astype("int8")
    return grid[["date", "store_nbr", *holiday_columns, "is_holiday", "holiday_scope_count"]]


def build_analysis_panel(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Create a validated full-grain panel while retaining missingness indicators."""
    train = datasets["train.csv"].copy()
    stores = datasets["stores.csv"].copy()
    transactions = datasets["transactions.csv"].copy()
    oil = datasets["oil.csv"].copy()
    holidays = datasets["holidays_events.csv"].copy()

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
    panel = train.merge(stores, on="store_nbr", how="left", validate="many_to_one")
    if panel[["city", "state", "type", "cluster"]].isna().any().any():
        raise ValueError("Store join left unmatched sales rows.")

    # A left join keeps every sales observation; missing traffic remains explicit.
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
    panel = add_date_features(panel)
    panel["promotion_intensity"] = np.log1p(panel["onpromotion"])

    # These assertions turn silent join errors into visible failures.
    if len(panel) != len(train):
        raise ValueError("A merge changed the sales-panel row count.")
    if panel.duplicated(["date", "store_nbr", "family"]).any():
        raise ValueError("The prepared panel is not unique at its intended grain.")
    return panel


def choose_analysis_scope(panel: pd.DataFrame) -> tuple[list[int], list[str], pd.Timestamp]:
    """Select well-covered representative stores, important families, and 24 months."""
    store_daily = panel.groupby(["store_nbr", "date"], as_index=False).agg(
        sales=("sales", "sum"), transactions=("transactions", "max")
    )
    store_metrics = store_daily.groupby("store_nbr").agg(
        sum=("sales", "sum"), mean=("sales", "mean"), std=("sales", "std"),
        transaction_coverage_pct=("transactions", lambda values: 100 * values.notna().mean()),
        active_sales_days_pct=("sales", lambda values: 100 * values.gt(0).mean()),
    )
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
    selections = [int(ranked.index[0]), int(ranked.index[1])]
    median_target = eligible["sum"].median()
    selections.append(int((eligible["sum"] - median_target).abs().idxmin()))
    selections.append(int(eligible["sum"].idxmin()))
    selections.append(int(eligible.loc[~eligible.index.isin(selections), "cv"].idxmax()))
    selected_stores = list(dict.fromkeys(selections))[:5]

    # Families combine commercial importance with one deliberately volatile case.
    family_daily = panel.groupby(["family", "date"], as_index=False)["sales"].sum()
    family_metrics = family_daily.groupby("family")["sales"].agg(["sum", "mean", "std"])
    family_metrics["cv"] = family_metrics["std"] / family_metrics["mean"]
    selected_families = list(family_metrics.nlargest(4, "sum").index)
    top_volume_pool = family_metrics.nlargest(15, "sum")
    volatility_choice = top_volume_pool.loc[
        ~top_volume_pool.index.isin(selected_families), "cv"
    ].idxmax()
    selected_families.append(str(volatility_choice))

    start_date = panel["date"].max() - pd.DateOffset(months=24) + pd.Timedelta(days=1)
    return selected_stores, selected_families, pd.Timestamp(start_date)
