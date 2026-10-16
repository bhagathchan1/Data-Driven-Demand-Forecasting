"""Advanced Exploratory Data Analysis (EDA) functions for retail demand.

This module provides operational and time-series analytical utilities:
    - Demand pattern classification using the Syntetos-Boylan (Croston) framework
      (Smooth, Intermittent, Erratic, Lumpy) based on ADI and CV^2.
    - Semi-monthly payday (Quincena: 15th & month-end) consumption surge analysis.
    - Macroeconomic and natural disaster shock analysis (April 2016 Ecuador earthquake).
    - Cross-category demand correlation and co-movement matrix.
    - Promotional elasticity and lift profiling across product categories.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# 1. Demand Pattern & Intermittency Classification (Syntetos-Boylan)
# ---------------------------------------------------------------------------

def classify_demand_patterns(
    panel: pd.DataFrame,
    group_cols: Sequence[str] = ("family",),
) -> pd.DataFrame:
    """Classify retail demand series using the Syntetos-Boylan / Croston framework.

    Categorizes demand streams into four distinct operational quadrants based on:
        - ADI (Average Demand Interval): Average time interval between non-zero demand days.
          Cutoff = 1.32 periods.
        - CV^2 (Squared Coefficient of Variation): Demand size variability during non-zero days.
          Cutoff = 0.49.

    Quadrants:
        - Smooth (ADI < 1.32, CV^2 < 0.49):
          Regular demand with low variation. Well-suited for standard moving averages and ARIMA.
        - Intermittent (ADI >= 1.32, CV^2 < 0.49):
          Sporadic demand but stable quantities when ordered. Well-suited for Croston's method.
        - Erratic (ADI < 1.32, CV^2 >= 0.49):
          Frequent demand with high size variation. Requires safety stock buffers.
        - Lumpy (ADI >= 1.32, CV^2 >= 0.49):
          Sporadic demand with highly volatile order sizes. Most difficult to forecast;
          requires specialized intermittent models and buffer management.

    Args:
        panel: DataFrame containing sales records with at least ['date', 'sales', *group_cols].
        group_cols: Columns defining individual series. Defaults to ("family",).

    Returns:
        pd.DataFrame: Summary table indexed by group_cols with columns:
            - 'total_periods': Total observed days
            - 'active_periods': Days with non-zero sales
            - 'zero_sales_pct': Percentage of days with zero sales
            - 'adi': Average Demand Interval (total_periods / active_periods)
            - 'cv2': Squared Coefficient of Variation of non-zero demand
            - 'demand_category': Quadrant label ('Smooth', 'Intermittent', 'Erratic', 'Lumpy')
    """
    records = []
    grouped = panel.groupby(list(group_cols), observed=True)

    for keys, group in grouped:
        sales = group["sales"].to_numpy()
        total_n = len(sales)
        non_zero = sales[sales > 0]
        n_positive = len(non_zero)

        if n_positive == 0:
            # Series with strictly 0 demand across the entire timeline
            adi = float("inf")
            cv2 = 0.0
            category = "Intermittent"
            zero_pct = 100.0
        else:
            # ADI: Average spacing between demand occurrences
            adi = total_n / n_positive
            # CV^2 of demand sizes when positive demand occurs
            mean_demand = non_zero.mean()
            std_demand = non_zero.std(ddof=1) if n_positive > 1 else 0.0
            cv2 = float((std_demand / mean_demand) ** 2) if mean_demand > 0 else 0.0
            zero_pct = 100.0 * (1.0 - (n_positive / total_n))

            # Syntetos-Boylan decision boundaries
            if adi < 1.32 and cv2 < 0.49:
                category = "Smooth"
            elif adi >= 1.32 and cv2 < 0.49:
                category = "Intermittent"
            elif adi < 1.32 and cv2 >= 0.49:
                category = "Erratic"
            else:
                category = "Lumpy"

        key_dict = dict(zip(group_cols, keys if isinstance(keys, tuple) else [keys]))
        records.append(
            {
                **key_dict,
                "total_periods": total_n,
                "active_periods": n_positive,
                "zero_sales_pct": round(zero_pct, 2),
                "adi": round(adi, 3),
                "cv2": round(cv2, 3),
                "demand_category": category,
            }
        )

    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# 2. Semi-Monthly Payday ("Quincena") Consumption Cycle Analysis
# ---------------------------------------------------------------------------

def analyze_payday_effects(panel: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Examine sales spikes associated with Ecuadorian bi-weekly paydays (Quincenas).

    In Ecuador, wages in public and formal private sectors are customarily paid
    on the 15th and on the last day of each calendar month. This creates
    recurring liquidity cycles that drive distinct surges in grocery spending.

    Args:
        panel: Sales panel DataFrame containing ['date', 'sales', 'store_nbr', 'family'].

    Returns:
        dict[str, pd.DataFrame]:
            - 'summary': Overall comparison of payday vs non-payday sales metrics.
            - 'by_family': Uplift ratios and volumes by product family.
            - 'by_store_type': Payday lift ratios across store formats (A, B, C, D, E).
    """
    df = panel.copy()
    dates = pd.to_datetime(df["date"])

    # Determine whether date is a payday (15th or end of month)
    is_15th = dates.dt.day.eq(15)
    is_month_end = dates.dt.is_month_end
    # Include the 16th and 1st as payday buffer days (weekend spillover / delayed shopping)
    is_payday_window = is_15th | is_month_end | dates.dt.day.isin([1, 16])
    df["is_payday"] = is_payday_window

    # Daily aggregated demand
    daily_network = df.groupby(["date", "is_payday"], observed=True)["sales"].sum().reset_index()

    summary = daily_network.groupby("is_payday")["sales"].agg(
        days="count",
        mean_daily_sales="mean",
        median_daily_sales="median",
        std_daily_sales="std",
    )
    if False in summary.index and True in summary.index:
        summary["lift_pct"] = round(
            100 * (summary.loc[True, "mean_daily_sales"] / summary.loc[False, "mean_daily_sales"] - 1), 2
        )

    # Family-level payday sensitivity
    family_payday = df.groupby(["family", "is_payday"], observed=True)["sales"].mean().unstack()
    family_payday.columns = ["regular_day_sales", "payday_sales"]
    family_payday["payday_lift_pct"] = round(
        100 * (family_payday["payday_sales"] / family_payday["regular_day_sales"] - 1), 2
    )
    family_payday = family_payday.sort_values("payday_lift_pct", ascending=False)

    # Store type payday sensitivity
    store_payday = df.groupby(["type", "is_payday"], observed=True)["sales"].mean().unstack()
    store_payday.columns = ["regular_day_sales", "payday_sales"]
    store_payday["payday_lift_pct"] = round(
        100 * (store_payday["payday_sales"] / store_payday["regular_day_sales"] - 1), 2
    )

    return {
        "summary": summary,
        "by_family": family_payday,
        "by_store_type": store_payday,
    }


# ---------------------------------------------------------------------------
# 3. Natural Disaster / Structural Shock Analysis (2016 Earthquake)
# ---------------------------------------------------------------------------

def analyze_earthquake_impact(
    panel: pd.DataFrame,
    window_days: int = 30,
) -> dict[str, pd.DataFrame]:
    """Analyze retail demand disruption caused by the April 16, 2016 Mw 7.8 earthquake.

    The earthquake was centered in the coastal provinces of Manabí and Esmeraldas,
    causing severe infrastructure damage, relief supply surges, and consumer shifts.
    This analysis compares the 30-day pre-earthquake window (2016-03-17 to 2016-04-15)
    with the 30-day post-earthquake window (2016-04-16 to 2016-05-15) across
    affected coastal stores versus the rest of the country.

    Args:
        panel: Sales panel with ['date', 'sales', 'state', 'family'].
        window_days: Number of days before and after the event to compare. Defaults to 30.

    Returns:
        dict[str, pd.DataFrame]:
            - 'regional_impact': Pre vs post mean daily sales by state/province.
            - 'family_shift': Changes in demand for essentials vs discretionary categories.
    """
    quake_date = pd.Timestamp("2016-04-16")
    pre_start = quake_date - pd.Timedelta(days=window_days)
    post_end = quake_date + pd.Timedelta(days=window_days)

    subset = panel.loc[
        panel["date"].ge(pre_start) & panel["date"].le(post_end)
    ].copy()

    # Assign period
    subset["period"] = np.where(subset["date"].lt(quake_date), "pre_quake", "post_quake")

    # Group by state
    regional = subset.groupby(["state", "period"], observed=True)["sales"].sum().unstack()
    regional["total_change_pct"] = round(
        100 * (regional["post_quake"] / regional["pre_quake"] - 1), 2
    )
    regional = regional.sort_values("total_change_pct", ascending=False)

    # Group by product family to identify emergency essentials surge vs discretionary decline
    family_impact = subset.groupby(["family", "period"], observed=True)["sales"].sum().unstack()
    family_impact["sales_change_pct"] = round(
        100 * (family_impact["post_quake"] / family_impact["pre_quake"] - 1), 2
    )
    family_impact = family_impact.sort_values("sales_change_pct", ascending=False)

    return {
        "regional_impact": regional,
        "family_shift": family_impact,
    }


# ---------------------------------------------------------------------------
# 4. Cross-Category Demand Correlation & Affinity
# ---------------------------------------------------------------------------

def compute_cross_family_correlations(panel: pd.DataFrame) -> pd.DataFrame:
    """Compute the Pearson correlation matrix of daily sales across product families.

    Aggregates network daily sales by category to identify clusters of product families
    that experience co-moving demand spikes (e.g., Grocery & Beverages) or independent behavior.

    Args:
        panel: Sales panel DataFrame with ['date', 'family', 'sales'].

    Returns:
        pd.DataFrame: Symmetrical correlation matrix of dimensions (n_families, n_families).
    """
    family_daily = panel.groupby(["date", "family"], observed=True)["sales"].sum().unstack()
    return family_daily.corr()


# ---------------------------------------------------------------------------
# 5. Promotional Elasticity & Uplift Analysis
# ---------------------------------------------------------------------------

def analyze_promotion_elasticity(panel: pd.DataFrame) -> pd.DataFrame:
    """Evaluate promotion participation, penetration, and sales uplift across families.

    Computes:
        - Active promotion days percentage (penetration rate)
        - Mean sales on promoted vs non-promoted days
        - Observed sales uplift multiplier (promoted / non-promoted ratio)
        - Mean promotion intensity (number of items on promotion when active)

    Args:
        panel: Sales panel DataFrame with ['family', 'sales', 'onpromotion'].

    Returns:
        pd.DataFrame: Summary table indexed by product family, sorted by volume uplift.
    """
    df = panel.copy()
    df["is_promoted"] = df["onpromotion"].gt(0)

    summary = df.groupby("family", observed=True).agg(
        total_sales=("sales", "sum"),
        promo_days_pct=("is_promoted", lambda values: round(100 * values.mean(), 2)),
        mean_items_when_promoted=("onpromotion", lambda values: round(values[values > 0].mean(), 1)),
    )

    # Calculate mean sales under promoted and non-promoted states
    promo_split = df.groupby(["family", "is_promoted"], observed=True)["sales"].mean().unstack()
    summary["mean_sales_non_promoted"] = promo_split[False].round(2)
    summary["mean_sales_promoted"] = promo_split[True].round(2)

    # Observed uplift ratio
    summary["uplift_ratio"] = (
        summary["mean_sales_promoted"] / summary["mean_sales_non_promoted"].replace(0, np.nan)
    ).round(2)

    return summary.sort_values("uplift_ratio", ascending=False)
