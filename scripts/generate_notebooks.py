"""Generate the project's six reproducible notebooks with nbformat."""

from pathlib import Path
import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"
NOTEBOOK_DIR.mkdir(exist_ok=True)


def md(text: str):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text: str):
    return nbf.v4.new_code_cell(text.strip())


def write_notebook(filename: str, cells: list) -> None:
    notebook = nbf.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.x"},
        },
    )
    nbf.write(notebook, NOTEBOOK_DIR / filename)


setup = """
from pathlib import Path
import sys
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
candidate = Path.cwd().resolve()
PROJECT_ROOT = next(
    path for path in (candidate, *candidate.parents)
    if (path / "data").is_dir() and (path / "src").is_dir()
)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DATA_DIR = PROJECT_ROOT / "outputs" / "processed_data"
FIGURE_DIR = PROJECT_ROOT / "reports" / "figures"
TABLE_DIR = PROJECT_ROOT / "reports" / "tables"
for directory in (PROCESSED_DATA_DIR, OUTPUT_DATA_DIR, FIGURE_DIR, TABLE_DIR):
    directory.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
"""


write_notebook(
    "01_data_understanding.ipynb",
    [
        md("""
# 01 — Data Understanding

## tl;dr

This notebook inventories and profiles the actual Kaggle files available locally. It establishes the grain, date coverage, candidate keys, missingness, duplicates, memory use, and descriptive context needed before cleaning or analysis. Conclusions here are deliberately preliminary.
        """),
        md("""
## Context & Methods

**Decision supported:** determine whether the source data is structurally suitable for retail demand and operations analysis.

### Key assumptions

- `sales` is observed sales, not unconstrained customer demand.
- A zero-sales row may reflect no demand, closure, or unavailable stock; the dataset cannot distinguish these directly.
- Candidate keys are validated empirically and are not treated as guaranteed database constraints.
- The Kaggle files in `data/raw/` are the controlling source for this notebook.
        """),
        code(setup),
        code("""
import numpy as np
import pandas as pd
from IPython.display import Markdown, display

from src.data_loader import (
    CANDIDATE_KEYS,
    DATASET_DESCRIPTIONS,
    EXPECTED_FILES,
    inspect_available_files,
    load_all_available,
    profile_dataset,
)

pd.set_option("display.max_columns", 20)
pd.set_option("display.float_format", lambda value: f"{value:,.3f}")
        """),
        md("## Data\n\n### 1. Verify available inputs"),
        code("""
inventory = inspect_available_files(RAW_DATA_DIR)
display(inventory)
missing_files = inventory.loc[~inventory["available"], "file"].tolist()
if missing_files:
    raise FileNotFoundError(f"Missing expected files: {missing_files}. See data/README.md.")
print(f"Verified {inventory['available'].sum()} of {len(EXPECTED_FILES)} expected files.")
        """),
        md("### 2. Load the available CSVs"),
        code("""
datasets = load_all_available(RAW_DATA_DIR)
profiles = pd.DataFrame(
    [profile_dataset(filename, frame) for filename, frame in datasets.items()]
)
display(profiles)
        """),
        md("""
**How to interpret this step:** row and column counts confirm the scale of each source, while memory usage indicates whether full-population analysis is practical. The tables are loaded independently here so that their grain is understood before any merge can silently multiply or remove records.
        """),
        md("### 3. Explain the datasets and their proposed grain"),
        code("""
grain_map = {
    "train.csv": "one date × store × product family",
    "test.csv": "one future date × store × product family",
    "stores.csv": "one store",
    "transactions.csv": "one date × store with a reported transaction count",
    "holidays_events.csv": "one holiday/event record; dates may repeat across events/scopes",
    "oil.csv": "one reported date",
    "sample_submission.csv": "one test-row id",
}
dataset_dictionary = pd.DataFrame(
    {
        "file": list(DATASET_DESCRIPTIONS),
        "represents": list(DATASET_DESCRIPTIONS.values()),
        "proposed_grain": [grain_map[name] for name in DATASET_DESCRIPTIONS],
        "candidate_key": [", ".join(CANDIDATE_KEYS[name]) for name in DATASET_DESCRIPTIONS],
    }
)
display(dataset_dictionary)
        """),
        md("## Results\n\n### 4. Columns and data types"),
        code("""
schema_rows = []
for filename, frame in datasets.items():
    for column, dtype in frame.dtypes.items():
        schema_rows.append({"file": filename, "column": column, "dtype": str(dtype)})
schema = pd.DataFrame(schema_rows)
display(schema)
        """),
        md("### 5. Date coverage, stores, and product families"),
        code("""
date_coverage = []
for filename, frame in datasets.items():
    if "date" in frame:
        date_coverage.append(
            {
                "file": filename,
                "start_date": frame["date"].min().date(),
                "end_date": frame["date"].max().date(),
                "unique_dates": frame["date"].nunique(),
                "invalid_dates": int(frame["date"].isna().sum()),
            }
        )
display(pd.DataFrame(date_coverage))

train = datasets["train.csv"]
stores = datasets["stores.csv"]
print(f"Training stores: {train['store_nbr'].nunique():,}")
print(f"Training product families: {train['family'].nunique():,}")
print(f"Store master rows: {len(stores):,}; unique store numbers: {stores['store_nbr'].nunique():,}")
display(pd.DataFrame({"product_family": sorted(train["family"].unique())}))
        """),
        md("### 6. Candidate-key, duplicate, and join checks"),
        code("""
key_checks = []
for filename, key in CANDIDATE_KEYS.items():
    frame = datasets[filename]
    key_checks.append(
        {
            "file": filename,
            "candidate_key": ", ".join(key),
            "duplicate_key_rows": int(frame.duplicated(key, keep=False).sum()),
            "exact_duplicate_rows": int(frame.duplicated().sum()),
        }
    )
display(pd.DataFrame(key_checks))

sales_key_duplicates = train.duplicated(["date", "store_nbr", "family"], keep=False).sum()
orphan_train_stores = len(set(train["store_nbr"]) - set(stores["store_nbr"]))
orphan_test_stores = len(set(datasets["test.csv"]["store_nbr"]) - set(stores["store_nbr"]))
print(f"Duplicate train date-store-family rows: {sales_key_duplicates:,}")
print(f"Training store keys absent from stores.csv: {orphan_train_stores:,}")
print(f"Test store keys absent from stores.csv: {orphan_test_stores:,}")
        """),
        md("""
**Why this matters operationally:** a demand-planning result is only credible if each sales observation represents one intended planning unit. Duplicate keys could double-count demand, while unmatched stores would remove geography, type, and cluster context from store comparisons.
        """),
        md("### 7. Missing values and memory usage"),
        code("""
missing_rows = []
for filename, frame in datasets.items():
    for column in frame.columns:
        count = int(frame[column].isna().sum())
        missing_rows.append(
            {
                "file": filename,
                "column": column,
                "missing_count": count,
                "missing_pct": 100 * count / len(frame),
            }
        )
missing_summary = pd.DataFrame(missing_rows)
display(missing_summary.loc[missing_summary["missing_count"].gt(0)])
display(profiles[["file", "rows", "columns", "memory_mb"]])
        """),
        md("### 8. Descriptive statistics"),
        code("""
for filename in ("train.csv", "transactions.csv", "oil.csv", "stores.csv"):
    print()
    print(filename)
    display(datasets[filename].describe(include="all").T)
        """),
        md("### 9. Domain-specific first checks"),
        code("""
holidays = datasets["holidays_events.csv"]
transactions = datasets["transactions.csv"]
oil = datasets["oil.csv"]
domain_checks = pd.DataFrame(
    [
        {"check": "negative sales rows", "value": int(train["sales"].lt(0).sum())},
        {"check": "zero sales rows", "value": int(train["sales"].eq(0).sum())},
        {"check": "negative promotion rows", "value": int(train["onpromotion"].lt(0).sum())},
        {"check": "negative transaction rows", "value": int(transactions["transactions"].lt(0).sum())},
        {"check": "oil rows with missing price", "value": int(oil["dcoilwtico"].isna().sum())},
        {"check": "additional holiday rows on repeated dates", "value": int(holidays.duplicated("date").sum())},
        {"check": "transferred holiday records", "value": int(holidays["transferred"].sum())},
    ]
)
display(domain_checks)
        """),
        md("""
**Why values are flagged rather than deleted:** retail extremes may be genuine operational signals. Zero sales can reflect low demand, closures, or stockouts; spikes can reflect promotions, holidays, paydays, or disruptions. Notebook 02 investigates these observations in context before applying any treatment.
        """),
        md("### 10. Small data dictionary"),
        code("""
data_dictionary = pd.DataFrame(
    [
        ("date", "Calendar date", "Shared time join; daily planning grain"),
        ("store_nbr", "Store identifier", "Joins sales/test/transactions to stores"),
        ("family", "Product-family category", "Category-level demand dimension"),
        ("sales", "Observed sales for a store-family-date", "Forecast target; may include fractional units"),
        ("onpromotion", "Number of promoted items in a family", "Promotion-intensity indicator, not causal assignment"),
        ("city / state", "Store geography", "Used for geographic and holiday-scope matching"),
        ("type", "Anonymized store type", "Store-format comparison dimension"),
        ("cluster", "Grouping of similar stores", "Store-segmentation dimension"),
        ("transactions", "Reported daily store transactions", "Traffic proxy at store-date grain"),
        ("holiday fields", "Event type, locale, description, transfer flag", "Context requiring scope-aware joins"),
        ("dcoilwtico", "WTI oil price", "Exploratory macro-context variable"),
    ],
    columns=["field", "meaning", "analytical_role"],
)
display(data_dictionary)
        """),
        md("### 11. Export small audit tables for report and presentation use"),
        code("""
profiles.to_csv(TABLE_DIR / "phase1_dataset_profile.csv", index=False)
pd.DataFrame(date_coverage).to_csv(TABLE_DIR / "phase1_date_coverage.csv", index=False)
pd.DataFrame(key_checks).to_csv(TABLE_DIR / "phase1_key_checks.csv", index=False)
domain_checks.to_csv(TABLE_DIR / "phase1_domain_checks.csv", index=False)
data_dictionary.to_csv(TABLE_DIR / "phase1_data_dictionary.csv", index=False)
print("Saved five compact Phase 1 audit tables to reports/tables/.")
        """),
        md("## Initial Data Observations"),
        code("""
expected_panel_rows = train["date"].nunique() * train["store_nbr"].nunique() * train["family"].nunique()
zero_rate = 100 * train["sales"].eq(0).mean()
oil_missing_rate = 100 * oil["dcoilwtico"].isna().mean()
display(Markdown(f'''
- All seven expected competition files are present locally.
- The training table has **{len(train):,} rows** from **{train['date'].min().date()} to {train['date'].max().date()}**, covering **{train['store_nbr'].nunique()} stores** and **{train['family'].nunique()} product families**.
- Its row count equals the complete date × store × family grid (**{expected_panel_rows:,}**), and no duplicate rows occur at that grain.
- There are no negative sales values, but **{train['sales'].eq(0).sum():,} rows ({zero_rate:.2f}%)** have zero sales. These require contextual review rather than automatic deletion.
- Oil price is the only source column with explicit nulls: **{oil['dcoilwtico'].isna().sum():,} rows ({oil_missing_rate:.2f}% of reported oil dates)**.
- Transaction records cover **{transactions['date'].nunique():,} dates** and are not a complete store-date grid; absence must be investigated before imputation.
- Holiday dates are not unique because several events or scopes can occur on the same date. These records must be aggregated or matched by national/regional/local scope before joining to sales.
- These are structural observations, not evidence of operational causes or performance differences.
'''))
        """),
        md("""
## Takeaways

- The core sales table is structurally complete at its stated grain and can support comparative analysis.
- Context tables cannot be merged naively: transactions are incomplete, oil needs time-aware treatment, and holiday scope can create join multiplication.
- Zero sales should be investigated, not deleted, because the dataset cannot distinguish low demand, closures, and stockouts.
- Notebook 02 will document cleaning choices, validate each merge, and select a detailed-analysis scope from observed volume, variability, and completeness.
        """),
        md("""
## PPT-ready Phase 1 message

**Slide headline:** The source data is structurally suitable for demand analysis, but contextual variables require careful preparation.

**Evidence to show:**

- 3.00 million daily store-family observations covering 54 stores and 33 product families.
- The sales panel is complete and unique at the date × store × family grain.
- 31.30% of rows report zero sales; these are retained for investigation rather than treated as errors.
- Oil-price gaps, incomplete transaction coverage, and overlapping holiday records require controlled, validated joins.

**Management interpretation:** the dataset can support demand-pattern and store/category comparisons, but it cannot directly reveal stockouts or optimize inventory because stock-on-hand, lead-time, service-level, cost, and margin data are absent.

**Do not claim yet:** promotion causality, holiday impact, store underperformance, or forecast improvement. Those require the later analytical phases.
        """),
    ],
)


write_notebook(
    "02_data_cleaning.ipynb",
    [
        md("""
# 02 — Data Cleaning and Preparation

## tl;dr

This notebook applies documented, non-destructive cleaning; constructs scope-aware holiday and daily oil features; validates merges; and selects a manageable 24-month analytical subset using observed sales volume and variability.
        """),
        md("""
## Context & Methods

Raw files remain unchanged. Outliers and zero sales are flagged and profiled rather than removed. Store, transaction, oil, and holiday data are attached with explicit join validation. The full panel is retained in memory for high-level checks; only the justified small subset is saved to avoid creating another large copy.

### Key assumptions

- Non-transferred national holidays apply to all stores; regional holidays match state; local holidays match city.
- Missing oil values are forward-filled on a daily calendar, with a start-boundary backfill only if needed; imputation is flagged.
- Missing transaction records are retained as missing, not converted to zero.
        """),
        code(setup),
        code("""
import json
import numpy as np
import pandas as pd
from IPython.display import Markdown, display

from src.data_loader import load_all_available
from src.preprocessing import build_analysis_panel, choose_analysis_scope

pd.set_option("display.float_format", lambda value: f"{value:,.3f}")
datasets = load_all_available(RAW_DATA_DIR)
train = datasets["train.csv"]
        """),
        md("## Data\n\n### 1. Systematic source-quality checks"),
        code("""
quality_checks = []
for filename, frame in datasets.items():
    quality_checks.append(
        {
            "file": filename,
            "rows": len(frame),
            "exact_duplicates": int(frame.duplicated().sum()),
            "missing_cells": int(frame.isna().sum().sum()),
            "invalid_dates": int(frame["date"].isna().sum()) if "date" in frame else 0,
        }
    )
display(pd.DataFrame(quality_checks))

print("Negative sales:", int(train["sales"].lt(0).sum()))
print("Zero sales:", f"{train['sales'].eq(0).sum():,}", f"({100*train['sales'].eq(0).mean():.2f}%)")
print("Negative promotions:", int(train["onpromotion"].lt(0).sum()))
print("Maximum onpromotion:", int(train["onpromotion"].max()))
        """),
        md("### 2. Investigate extremes without deleting them"),
        code("""
sales_quantiles = train["sales"].quantile([0, .5, .9, .95, .99, .999, 1]).rename("sales")
promotion_quantiles = train["onpromotion"].quantile([0, .5, .9, .95, .99, .999, 1]).rename("onpromotion")
display(pd.concat([sales_quantiles, promotion_quantiles], axis=1))

extreme_threshold = train["sales"].quantile(.999)
extreme_rows = train.loc[train["sales"].ge(extreme_threshold)].copy()
extreme_context = (
    extreme_rows.groupby("family")["sales"]
    .agg(extreme_rows="size", median_extreme_sales="median", max_sales="max")
    .sort_values("extreme_rows", ascending=False)
    .head(10)
)
display(extreme_context)
print("Decision: retain extremes; later notebooks test holiday, promotion, timing, and family context.")
        """),
        md("### 3. Inspect oil, holidays, and transactions before integration"),
        code("""
oil = datasets["oil.csv"]
holidays = datasets["holidays_events.csv"]
transactions = datasets["transactions.csv"]

context_quality = pd.DataFrame(
    [
        ("oil missing price", int(oil["dcoilwtico"].isna().sum()), 100 * oil["dcoilwtico"].isna().mean()),
        ("holiday exact duplicates", int(holidays.duplicated().sum()), 100 * holidays.duplicated().mean()),
        ("holiday extra rows on repeated dates", int(holidays.duplicated("date").sum()), 100 * holidays.duplicated("date").mean()),
        ("transaction exact duplicates", int(transactions.duplicated().sum()), 100 * transactions.duplicated().mean()),
        ("transaction negative counts", int(transactions["transactions"].lt(0).sum()), 100 * transactions["transactions"].lt(0).mean()),
    ],
    columns=["check", "count", "pct_of_source_rows"],
)
display(context_quality)
display(holidays.groupby(["locale", "type", "transferred"]).size().rename("records").reset_index())
        """),
        md("## Results\n\n### 4. Build and validate the integrated panel"),
        code("""
panel = build_analysis_panel(datasets)
print(f"Rows before merge: {len(train):,}")
print(f"Rows after merge:  {len(panel):,}")
print("Unique date-store-family key:", not panel.duplicated(["date", "store_nbr", "family"]).any())
print("Missing store attributes:", int(panel[["city", "state", "type", "cluster"]].isna().sum().sum()))
print("Missing oil after daily fill:", int(panel["dcoilwtico"].isna().sum()))
print("Sales rows whose store-date lacks transactions:", f"{panel['transaction_record_missing'].sum():,}")
display(panel.head())
        """),
        md("### 5. Explain missing transaction coverage"),
        code("""
store_date = panel.groupby(["store_nbr", "date"], observed=True).agg(
    sales=("sales", "sum"),
    transactions=("transactions", "max"),
).reset_index()
missing_tx = store_date.loc[store_date["transactions"].isna()]
tx_by_store = store_date.groupby("store_nbr").agg(
    observed_store_dates=("date", "size"),
    transaction_coverage_pct=("transactions", lambda values: 100 * values.notna().mean()),
    first_positive_sales_date=("date", "min"),
).sort_values("transaction_coverage_pct")
display(tx_by_store.head(10))
print(f"Missing transaction store-dates: {len(missing_tx):,} of {len(store_date):,} ({100*len(missing_tx)/len(store_date):.2f}%)")
print("Decision: retain missingness; do not interpret missing transaction rows as zero traffic.")
        """),
        md("### 6. Select the detailed-analysis scope from observed evidence"),
        code("""
selected_stores, selected_families, scope_start = choose_analysis_scope(panel)
scope_end = panel["date"].max()

store_daily = panel.groupby(["store_nbr", "date"], observed=True)["sales"].sum().reset_index()
store_metrics = store_daily.groupby("store_nbr")["sales"].agg(total_sales="sum", mean_daily_sales="mean", std_daily_sales="std")
store_metrics["cv"] = store_metrics["std_daily_sales"] / store_metrics["mean_daily_sales"]

family_daily = panel.groupby(["family", "date"], observed=True)["sales"].sum().reset_index()
family_metrics = family_daily.groupby("family", observed=True)["sales"].agg(total_sales="sum", mean_daily_sales="mean", std_daily_sales="std")
family_metrics["cv"] = family_metrics["std_daily_sales"] / family_metrics["mean_daily_sales"]

display(store_metrics.loc[selected_stores].sort_values("total_sales", ascending=False))
display(family_metrics.loc[selected_families].sort_values("total_sales", ascending=False))
print("Selected stores:", selected_stores)
print("Selected families:", selected_families)
print("Detailed period:", scope_start.date(), "to", scope_end.date())
        """),
        md("### 7. Save only the manageable analysis subset and scope metadata"),
        code("""
subset = panel.loc[
    panel["store_nbr"].isin(selected_stores)
    & panel["family"].isin(selected_families)
    & panel["date"].between(scope_start, scope_end)
].copy()

subset_path = OUTPUT_DATA_DIR / "analysis_subset.csv.gz"
subset.to_csv(subset_path, index=False, compression="gzip")
scope = {
    "selected_stores": selected_stores,
    "selected_families": selected_families,
    "start_date": scope_start.strftime("%Y-%m-%d"),
    "end_date": scope_end.strftime("%Y-%m-%d"),
    "selection_logic": (
        "Stores: two highest-volume, one median-volume, one lowest-volume, and one remaining high-CV store. "
        "Families: four highest-volume plus the highest-CV family among the top 15 by volume."
    ),
}
(OUTPUT_DATA_DIR / "analysis_scope.json").write_text(json.dumps(scope, indent=2))
print(f"Saved {len(subset):,} rows to {subset_path.relative_to(PROJECT_ROOT)}")
print(f"Subset size: {subset_path.stat().st_size / 1024**2:.2f} MiB compressed")
        """),
        md("## Takeaways"),
        code("""
display(Markdown(f'''
- The cleaned integration preserves all **{len(panel):,}** training rows and the intended date-store-family key.
- No negative sales or promotion values were found; no rows were removed as outliers.
- **{100*panel['transaction_record_missing'].mean():.2f}% of sales rows** inherit a missing transaction record at their store-date. This is retained as missing and flagged.
- Oil is aligned to a daily calendar and filled from prior information, with an explicit imputation flag.
- Holidays are matched to stores by national, regional, and local scope, avoiding a many-to-many date-only join.
- Detailed analysis uses **{len(selected_stores)} stores**, **{len(selected_families)} families**, and the final **24 months**, selected through transparent volume and variability criteria.
- The full panel is rebuilt from raw inputs when needed; only the **{len(subset):,}-row** subset is saved, avoiding a large duplicate of the raw sales data.
'''))
        """),
    ],
)


write_notebook(
    "03_exploratory_data_analysis.ipynb",
    [
        md("""
# 03 — Exploratory Data Analysis

## tl;dr

This notebook examines overall demand, stores, product families, promotions, holidays, transactions, and oil prices. It prioritizes interpretable patterns and operational relevance. All relationships are descriptive; promotion, holiday, transaction, and oil comparisons are not causal estimates.
        """),
        md("""
## Context & Methods

High-level analysis uses the full sales panel. Detailed store-family views use the justified subset selected in Notebook 02. Daily averages are preferred when month length or partial periods could distort totals.

### Key assumptions

- Sales aggregate mixed unit types across product families, so portfolio-level totals are an index of activity rather than a common physical unit.
- Promotion comparisons are exposed to selection bias because promotions are not randomly assigned.
- Sales per transaction is a descriptive basket proxy, not revenue or margin per customer.
        """),
        code(setup),
        code("""
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import Markdown, display

from src.data_loader import load_all_available
from src.preprocessing import build_analysis_panel
from src.visualization import PROJECT_COLORS, save_figure, set_project_style

set_project_style()
pd.set_option("display.float_format", lambda value: f"{value:,.3f}")
datasets = load_all_available(RAW_DATA_DIR)
panel = build_analysis_panel(datasets)
scope = json.loads((OUTPUT_DATA_DIR / "analysis_scope.json").read_text())
selected_stores = scope["selected_stores"]
selected_families = scope["selected_families"]
        """),
        md("## Results\n\n### 1. Overall demand trend and rolling average"),
        code("""
daily_total = panel.groupby("date", observed=True)["sales"].sum().sort_index()
rolling_28 = daily_total.rolling(28, min_periods=14).mean()
fig, ax = plt.subplots(figsize=(13, 6))
ax.plot(daily_total.index, daily_total, color="#9bb7d3", linewidth=.7, label="Daily sales")
ax.plot(rolling_28.index, rolling_28, color=PROJECT_COLORS[0], linewidth=2, label="28-day moving average")
ax.set(title="Total observed sales over time", xlabel="Date", ylabel="Sales (mixed units)")
ax.legend()
save_figure(fig, FIGURE_DIR, "eda_01_total_sales_trend.png")
plt.show()
        """),
        md("### 2. Year, month, and weekday patterns"),
        code("""
calendar_daily = daily_total.rename("sales").reset_index()
calendar_daily["year"] = calendar_daily["date"].dt.year
calendar_daily["month"] = calendar_daily["date"].dt.month
calendar_daily["day_of_week"] = calendar_daily["date"].dt.dayofweek

yearly = calendar_daily.groupby("year").agg(total_sales=("sales", "sum"), mean_daily_sales=("sales", "mean"), days=("date", "nunique"))
monthly = calendar_daily.groupby("month")["sales"].mean()
weekday = calendar_daily.groupby("day_of_week")["sales"].mean().reindex(range(7))
weekday.index = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
display(yearly)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
monthly.plot(kind="bar", ax=axes[0], color=PROJECT_COLORS[0])
axes[0].set(title="Average daily sales by calendar month", xlabel="Month", ylabel="Average daily sales")
weekday.plot(kind="bar", ax=axes[1], color=PROJECT_COLORS[1])
axes[1].set(title="Average daily sales by weekday", xlabel="Weekday", ylabel="Average daily sales")
fig.tight_layout()
save_figure(fig, FIGURE_DIR, "eda_02_calendar_patterns.png")
plt.show()
        """),
        md("### 3. Store ranking, type, cluster, and geography"),
        code("""
store_daily = panel.groupby(["store_nbr", "date"], observed=True).agg(
    sales=("sales", "sum"), transactions=("transactions", "max")
).reset_index()
store_summary = store_daily.groupby("store_nbr").agg(
    total_sales=("sales", "sum"),
    mean_daily_sales=("sales", "mean"),
    std_daily_sales=("sales", "std"),
    transaction_coverage_pct=("transactions", lambda values: 100 * values.notna().mean()),
    total_transactions=("transactions", "sum"),
)
store_summary["cv"] = store_summary["std_daily_sales"] / store_summary["mean_daily_sales"]
store_summary["sales_per_transaction_proxy"] = store_summary["total_sales"] / store_summary["total_transactions"]
store_summary = store_summary.join(datasets["stores.csv"].set_index("store_nbr"))
display(store_summary.nlargest(10, "total_sales"))

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
store_summary.nlargest(15, "total_sales").sort_values("total_sales")["total_sales"].plot(
    kind="barh", ax=axes[0], color=PROJECT_COLORS[0]
)
axes[0].set(title="Top 15 stores by total observed sales", xlabel="Sales (mixed units)", ylabel="Store")
store_summary.groupby("type", observed=True)["mean_daily_sales"].mean().sort_values().plot(
    kind="barh", ax=axes[1], color=PROJECT_COLORS[1]
)
axes[1].set(title="Average daily store sales by store type", xlabel="Average daily sales", ylabel="Store type")
fig.tight_layout()
save_figure(fig, FIGURE_DIR, "eda_03_store_performance.png")
plt.show()

geo_summary = store_summary.groupby("state", observed=True).agg(
    stores=("total_sales", "size"), total_sales=("total_sales", "sum"), mean_store_daily_sales=("mean_daily_sales", "mean")
).sort_values("total_sales", ascending=False)
cluster_summary = store_summary.groupby("cluster", observed=True).agg(
    stores=("total_sales", "size"), mean_store_daily_sales=("mean_daily_sales", "mean"), mean_cv=("cv", "mean")
).sort_values("mean_store_daily_sales", ascending=False)
display(geo_summary.head(10))
display(cluster_summary)
        """),
        md("### 4. Product-family importance, variability, and growth"),
        code("""
family_daily = panel.groupby(["family", "date"], observed=True)["sales"].sum().reset_index()
family_summary = family_daily.groupby("family", observed=True)["sales"].agg(
    total_sales="sum", mean_daily_sales="mean", std_daily_sales="std"
)
family_summary["cv"] = family_summary["std_daily_sales"] / family_summary["mean_daily_sales"]
family_summary["sales_share_pct"] = 100 * family_summary["total_sales"] / family_summary["total_sales"].sum()

first_year = panel["year"].min()
last_full_year = panel.loc[panel["year"].lt(panel["year"].max()), "year"].max()
family_year = panel.groupby(["family", "year"], observed=True)["sales"].sum().unstack(fill_value=0)
family_summary["growth_first_to_last_full_year_pct"] = 100 * (
    family_year[last_full_year] / family_year[first_year].replace(0, np.nan) - 1
)
display(family_summary.sort_values("total_sales", ascending=False).head(15))

fig, axes = plt.subplots(1, 2, figsize=(14, 7))
family_summary.nlargest(15, "total_sales").sort_values("total_sales")["total_sales"].plot(
    kind="barh", ax=axes[0], color=PROJECT_COLORS[0]
)
axes[0].set(title="Top 15 product families by total sales", xlabel="Sales (mixed units)", ylabel="Family")
axes[1].scatter(family_summary["mean_daily_sales"], family_summary["cv"], color=PROJECT_COLORS[4], alpha=.8)
for family in family_summary.nlargest(5, "total_sales").index:
    axes[1].annotate(family, (family_summary.loc[family, "mean_daily_sales"], family_summary.loc[family, "cv"]), fontsize=8)
axes[1].set(title="Family demand level versus variability", xlabel="Mean daily sales", ylabel="Coefficient of variation")
fig.tight_layout()
save_figure(fig, FIGURE_DIR, "eda_04_family_importance_variability.png")
plt.show()
        """),
        md("### 5. Detailed store-family comparison for the justified subset"),
        code("""
scope_panel = panel.loc[
    panel["store_nbr"].isin(selected_stores) & panel["family"].isin(selected_families)
]
store_family = scope_panel.groupby(["store_nbr", "family"], observed=True)["sales"].sum().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(12, 6))
image = ax.imshow(store_family, aspect="auto", cmap="Blues")
ax.set_xticks(range(len(store_family.columns)), labels=store_family.columns, rotation=45, ha="right")
ax.set_yticks(range(len(store_family.index)), labels=store_family.index)
ax.set(title="Sales concentration across selected stores and families", xlabel="Product family", ylabel="Store")
fig.colorbar(image, ax=ax, label="Total sales (mixed units)")
fig.tight_layout()
save_figure(fig, FIGURE_DIR, "eda_05_store_family_heatmap.png")
plt.show()
        """),
        md("### 6. Promotion association and heterogeneity"),
        code("""
promotion_comparison = panel.assign(promoted=panel["onpromotion"].gt(0)).groupby(
    ["family", "promoted"], observed=True
)["sales"].mean().unstack()
promotion_comparison.columns = ["mean_sales_not_promoted", "mean_sales_promoted"]
promotion_comparison["promoted_to_nonpromoted_ratio"] = (
    promotion_comparison["mean_sales_promoted"] / promotion_comparison["mean_sales_not_promoted"].replace(0, np.nan)
)
promotion_comparison["promotion_coverage_pct"] = panel.groupby("family", observed=True)["onpromotion"].apply(
    lambda values: 100 * values.gt(0).mean()
)
display(promotion_comparison.sort_values("promoted_to_nonpromoted_ratio", ascending=False).head(15))

plot_promo = promotion_comparison.loc[family_summary.nlargest(12, "total_sales").index].sort_values("promoted_to_nonpromoted_ratio")
fig, ax = plt.subplots(figsize=(11, 7))
plot_promo["promoted_to_nonpromoted_ratio"].plot(kind="barh", ax=ax, color=PROJECT_COLORS[3])
ax.axvline(1, color="black", linestyle="--", linewidth=1)
ax.set(title="Observed promoted/non-promoted mean-sales ratio — top families", xlabel="Ratio (association, not causal lift)", ylabel="Family")
save_figure(fig, FIGURE_DIR, "eda_06_promotion_association.png")
plt.show()

store_promo = panel.assign(promoted=panel["onpromotion"].gt(0)).groupby(
    ["store_nbr", "promoted"], observed=True
)["sales"].mean().unstack()
store_promo["ratio"] = store_promo[True] / store_promo[False].replace(0, np.nan)
display(store_promo["ratio"].sort_values(ascending=False).head(10).rename("promoted_to_nonpromoted_ratio"))
        """),
        md("### 7. Holidays and major events"),
        code("""
store_date = panel.groupby(["store_nbr", "date"], observed=True).agg(
    sales=("sales", "sum"),
    is_holiday=("is_holiday", "max"),
    is_national_holiday=("is_national_holiday", "max"),
    is_regional_holiday=("is_regional_holiday", "max"),
    is_local_holiday=("is_local_holiday", "max"),
).reset_index()
holiday_comparison = store_date.groupby("is_holiday")["sales"].agg(["count", "mean", "median", "std"])
display(holiday_comparison)

scope_means = {}
for column in ("is_national_holiday", "is_regional_holiday", "is_local_holiday"):
    scope_means[column] = store_date.groupby(column)["sales"].mean().to_dict()
display(pd.DataFrame(scope_means).T.rename(columns={False: "normal_or_other", True: "flagged_scope"}))

daily_event = datasets["holidays_events.csv"].loc[
    ~datasets["holidays_events.csv"]["transferred"]
].groupby("date")["description"].agg(lambda values: " | ".join(sorted(set(values))))
daily_sales = daily_total.to_frame().join(daily_event).dropna()
display(daily_sales.nlargest(12, "sales"))
        """),
        md("### 8. Transactions, traffic, and the sales-per-transaction proxy"),
        code("""
traffic = panel.groupby(["date", "store_nbr"], observed=True).agg(
    sales=("sales", "sum"), transactions=("transactions", "max")
).dropna().reset_index()
traffic["sales_per_transaction_proxy"] = traffic["sales"] / traffic["transactions"].replace(0, np.nan)
traffic_correlation = traffic[["sales", "transactions"]].corr().iloc[0, 1]
print(f"Store-day Pearson correlation between sales and transactions: {traffic_correlation:.3f}")

sample = traffic.sample(min(12000, len(traffic)), random_state=RANDOM_SEED)
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].scatter(sample["transactions"], sample["sales"], s=8, alpha=.18, color=PROJECT_COLORS[0])
axes[0].set(title="Store-day transactions and observed sales", xlabel="Transactions", ylabel="Sales (mixed units)")
store_summary.sort_values("sales_per_transaction_proxy")["sales_per_transaction_proxy"].plot(
    kind="bar", ax=axes[1], color=PROJECT_COLORS[1]
)
axes[1].set(title="Sales-per-transaction proxy by store", xlabel="Store", ylabel="Mixed sales units per transaction")
axes[1].tick_params(axis="x", labelsize=7)
fig.tight_layout()
save_figure(fig, FIGURE_DIR, "eda_07_transactions.png")
plt.show()
        """),
        md("### 9. Oil prices as exploratory context"),
        code("""
oil_daily = panel.groupby("date", observed=True).agg(
    sales=("sales", "sum"), dcoilwtico=("dcoilwtico", "max")
).reset_index()
oil_monthly = oil_daily.set_index("date").resample("MS").mean()
oil_corr = oil_monthly[["sales", "dcoilwtico"]].corr().iloc[0, 1]
print(f"Monthly contemporaneous correlation: {oil_corr:.3f} (descriptive only)")

fig, ax1 = plt.subplots(figsize=(12, 5))
ax1.plot(oil_monthly.index, oil_monthly["sales"], color=PROJECT_COLORS[0], label="Average daily sales")
ax1.set(xlabel="Month", ylabel="Average daily sales")
ax2 = ax1.twinx()
ax2.plot(oil_monthly.index, oil_monthly["dcoilwtico"], color=PROJECT_COLORS[4], label="WTI oil price", alpha=.8)
ax2.set_ylabel("WTI price")
ax1.set_title("Sales and oil prices over time — exploratory context")
lines = ax1.get_lines() + ax2.get_lines()
ax1.legend(lines, [line.get_label() for line in lines], loc="upper left")
save_figure(fig, FIGURE_DIR, "eda_08_oil_context.png")
plt.show()
        """),
        md("### 10. Save compact evidence tables"),
        code("""
store_summary.reset_index().to_csv(TABLE_DIR / "store_summary.csv", index=False)
family_summary.reset_index().to_csv(TABLE_DIR / "family_summary.csv", index=False)
promotion_comparison.reset_index().to_csv(TABLE_DIR / "promotion_summary.csv", index=False)
yearly.reset_index().to_csv(TABLE_DIR / "yearly_summary.csv", index=False)
holiday_comparison.reset_index().to_csv(TABLE_DIR / "holiday_summary.csv", index=False)
print("Saved five compact evidence tables to reports/tables/.")
        """),
        md("## Takeaways"),
        code("""
top_store = store_summary["total_sales"].idxmax()
top_family = family_summary["total_sales"].idxmax()
peak_weekday = weekday.idxmax()
peak_month = int(monthly.idxmax())
display(Markdown(f'''
- **Store {top_store}** has the highest total observed sales; store scale and variability differ materially across the network.
- **{top_family}** contributes the most family-level sales, while family CV shows that importance and predictability are separate operational dimensions.
- Average daily demand is highest on **{peak_weekday}** and in calendar month **{peak_month}**, which motivates differentiated staffing and replenishment review.
- Promoted rows often have higher mean sales, but the ratio varies by family and store and must be treated as association rather than incremental causal lift.
- Holiday effects vary by scope; date-only joins would obscure local and regional relevance.
- Transactions and sales move together (store-day correlation **{traffic_correlation:.3f}**), but the mixed-unit sales-per-transaction measure is only a basket proxy.
- The monthly sales/oil correlation is **{oil_corr:.3f}** and is exploratory; shared trends and omitted factors prevent causal interpretation.
'''))
        """),
    ],
)


write_notebook(
    "04_operations_analysis.ipynb",
    [
        md("""
# 04 — Operations Analysis

## tl;dr

This notebook turns demand evidence into operational diagnostics: stable/volatile family segments, store performance profiles, promotion dependence indicators, and peak-demand windows. Recommendations are framed as planning actions, not precise inventory optimization.
        """),
        md("""
## Context & Methods

Demand variability is measured on daily aggregates using coefficient of variation (CV = standard deviation / mean). Median demand and median CV create transparent four-quadrant family segments. These are relative portfolio segments, not universal industry thresholds.
        """),
        code(setup),
        code("""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import Markdown, display

from src.data_loader import load_all_available
from src.preprocessing import build_analysis_panel
from src.visualization import PROJECT_COLORS, save_figure, set_project_style

set_project_style()
pd.set_option("display.float_format", lambda value: f"{value:,.3f}")
datasets = load_all_available(RAW_DATA_DIR)
panel = build_analysis_panel(datasets)
        """),
        md("## Results\n\n### 1. Family demand variability and operational segments"),
        code("""
family_daily = panel.groupby(["family", "date"], observed=True)["sales"].sum().reset_index()
family_ops = family_daily.groupby("family", observed=True)["sales"].agg(
    mean_daily_demand="mean", std_daily_demand="std", total_sales="sum"
)
family_ops["cv"] = family_ops["std_daily_demand"] / family_ops["mean_daily_demand"]
demand_cut = family_ops["mean_daily_demand"].median()
cv_cut = family_ops["cv"].median()
family_ops["demand_level"] = np.where(family_ops["mean_daily_demand"].ge(demand_cut), "High demand", "Low demand")
family_ops["variability_level"] = np.where(family_ops["cv"].ge(cv_cut), "Volatile", "Stable")
family_ops["segment"] = family_ops["demand_level"] + " / " + family_ops["variability_level"]
display(family_ops.sort_values(["segment", "total_sales"], ascending=[True, False]))

fig, ax = plt.subplots(figsize=(11, 7))
segment_colors = {
    "High demand / Stable": PROJECT_COLORS[1], "High demand / Volatile": PROJECT_COLORS[4],
    "Low demand / Stable": PROJECT_COLORS[0], "Low demand / Volatile": PROJECT_COLORS[3],
}
for segment, values in family_ops.groupby("segment"):
    ax.scatter(values["mean_daily_demand"], values["cv"], label=segment, s=65, alpha=.8, color=segment_colors[segment])
ax.axvline(demand_cut, color="grey", linestyle="--")
ax.axhline(cv_cut, color="grey", linestyle="--")
for family in family_ops.nlargest(6, "total_sales").index:
    ax.annotate(family, (family_ops.loc[family, "mean_daily_demand"], family_ops.loc[family, "cv"]), fontsize=8)
ax.set(title="Product-family demand segmentation", xlabel="Mean daily demand", ylabel="Coefficient of variation")
ax.legend()
save_figure(fig, FIGURE_DIR, "operations_01_family_segments.png")
plt.show()
        """),
        md("### 2. Store performance and operating profiles"),
        code("""
store_daily = panel.groupby(["store_nbr", "date"], observed=True).agg(
    sales=("sales", "sum"), transactions=("transactions", "max"), onpromotion=("onpromotion", "sum")
).reset_index()
store_ops = store_daily.groupby("store_nbr").agg(
    average_daily_sales=("sales", "mean"),
    std_daily_sales=("sales", "std"),
    average_daily_transactions=("transactions", "mean"),
    transaction_coverage_pct=("transactions", lambda values: 100 * values.notna().mean()),
    promoted_item_days=("onpromotion", lambda values: values.gt(0).sum()),
    observed_days=("date", "size"),
)
store_ops["demand_cv"] = store_ops["std_daily_sales"] / store_ops["average_daily_sales"]
store_ops["promotion_active_days_pct"] = 100 * store_ops["promoted_item_days"] / store_ops["observed_days"]

monthly_store = store_daily.assign(month=store_daily["date"].dt.month).groupby(["store_nbr", "month"])["sales"].mean()
store_ops["seasonal_sensitivity"] = monthly_store.groupby("store_nbr").max() / monthly_store.groupby("store_nbr").mean()
store_ops = store_ops.join(datasets["stores.csv"].set_index("store_nbr"))
display(store_ops.sort_values("average_daily_sales", ascending=False).head(15))

fig, ax = plt.subplots(figsize=(11, 7))
scatter = ax.scatter(
    store_ops["average_daily_sales"], store_ops["demand_cv"],
    s=20 + 2 * store_ops["average_daily_transactions"].fillna(0) ** .5,
    c=store_ops["promotion_active_days_pct"], cmap="viridis", alpha=.8
)
ax.set(title="Store operating profiles", xlabel="Average daily sales", ylabel="Demand CV")
fig.colorbar(scatter, ax=ax, label="Promotion-active days (%)")
save_figure(fig, FIGURE_DIR, "operations_02_store_profiles.png")
plt.show()
        """),
        md("### 3. Promotion planning indicators"),
        code("""
promo = panel.assign(promoted=panel["onpromotion"].gt(0)).groupby(
    ["family", "promoted"], observed=True
)["sales"].agg(["mean", "median", "count"]).unstack()
promo_metrics = pd.DataFrame(index=promo.index)
promo_metrics["mean_not_promoted"] = promo[("mean", False)]
promo_metrics["mean_promoted"] = promo[("mean", True)]
promo_metrics["observed_ratio"] = promo_metrics["mean_promoted"] / promo_metrics["mean_not_promoted"].replace(0, np.nan)
promo_metrics["promoted_observations"] = promo[("count", True)]
promo_metrics = promo_metrics.join(family_ops[["segment", "total_sales"]])
display(promo_metrics.sort_values("observed_ratio", ascending=False).head(15))

fig, ax = plt.subplots(figsize=(11, 7))
promo_metrics.nlargest(15, "total_sales").sort_values("observed_ratio")["observed_ratio"].plot(
    kind="barh", ax=ax, color=PROJECT_COLORS[3]
)
ax.axvline(1, color="black", linestyle="--", linewidth=1)
ax.set(title="Promotion association among high-volume families", xlabel="Promoted/non-promoted mean-sales ratio", ylabel="Family")
save_figure(fig, FIGURE_DIR, "operations_03_promotion_planning.png")
plt.show()
        """),
        md("### 4. Peak-demand calendar for staffing and capacity"),
        code("""
network_daily = panel.groupby("date", observed=True).agg(
    sales=("sales", "sum"), is_holiday=("is_holiday", "max"), onpromotion=("onpromotion", "sum")
).reset_index()
network_daily["weekday"] = network_daily["date"].dt.day_name()
network_daily["month"] = network_daily["date"].dt.month
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

peak_weekdays = network_daily.groupby("weekday")["sales"].agg(["mean", "std"]).reindex(weekday_order)
peak_months = network_daily.groupby("month")["sales"].agg(["mean", "std"])
holiday_peak = network_daily.groupby("is_holiday")["sales"].agg(["mean", "median", "std", "count"])
promotion_bins = pd.qcut(network_daily["onpromotion"], 4, duplicates="drop")
promotion_peak = network_daily.groupby(promotion_bins, observed=True)["sales"].agg(["mean", "median", "count"])
display(peak_weekdays.sort_values("mean", ascending=False))
display(peak_months.sort_values("mean", ascending=False))
display(holiday_peak)
display(promotion_peak)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
peak_weekdays["mean"].plot(kind="bar", ax=axes[0], color=PROJECT_COLORS[0])
axes[0].set(title="Average network demand by weekday", xlabel="Weekday", ylabel="Average daily sales")
peak_months["mean"].plot(kind="bar", ax=axes[1], color=PROJECT_COLORS[1])
axes[1].set(title="Average network demand by month", xlabel="Month", ylabel="Average daily sales")
fig.tight_layout()
save_figure(fig, FIGURE_DIR, "operations_04_peak_calendar.png")
plt.show()
        """),
        md("### 5. Save operational evidence tables"),
        code("""
family_ops.reset_index().to_csv(TABLE_DIR / "family_operations_segments.csv", index=False)
store_ops.reset_index().to_csv(TABLE_DIR / "store_operations_summary.csv", index=False)
promo_metrics.reset_index().to_csv(TABLE_DIR / "promotion_operations_summary.csv", index=False)
peak_weekdays.reset_index().to_csv(TABLE_DIR / "peak_weekdays.csv", index=False)
peak_months.reset_index().to_csv(TABLE_DIR / "peak_months.csv", index=False)
print("Saved five operations evidence tables.")
        """),
        md("## Takeaways — implications and possible actions"),
        code("""
segment_counts = family_ops["segment"].value_counts()
peak_day = peak_weekdays["mean"].idxmax()
peak_month = int(peak_months["mean"].idxmax())
most_variable_store = int(store_ops["demand_cv"].idxmax())
display(Markdown(f'''
- **Finding:** Family segments contain {segment_counts.to_dict()}. **Implication:** demand level and variability require different controls. **Possible action:** use routine replenishment for stable families and shorter review cycles or buffers for volatile families, subject to lead-time and stock data.
- **Finding:** Store {most_variable_store} has the highest daily-demand CV. **Implication:** network-wide averages may understate local planning uncertainty. **Possible action:** use store-specific staffing and replenishment tolerances.
- **Finding:** The highest average network demand occurs on **{peak_day}** and in month **{peak_month}**. **Implication:** capacity requirements are not uniform. **Possible action:** review labor rosters, receiving capacity, and supplier schedules ahead of recurring peaks.
- **Finding:** Promotion-associated sales ratios vary across families. **Implication:** a single promotion rule is unlikely to fit the portfolio. **Possible action:** prioritize controlled evaluation by category and store rather than interpreting descriptive ratios as causal lift.
- **Limitation:** Exact safety stocks, reorder points, or service-level gains cannot be calculated without inventory positions, stockouts, lead times, costs, and service targets.
'''))
        """),
    ],
)


write_notebook(
    "05_forecasting.ipynb",
    [
        md("""
# 05 — Forecasting for Operational Planning

## tl;dr

This notebook evaluates whether transparent forecasts improve on simple operational baselines for selected daily store-family series. It uses a chronological 60-day holdout and compares naive, weekly seasonal-naive, Holt-Winters, and Random Forest approaches. The purpose is planning support, not leaderboard optimization.
        """),
        md("""
## Context & Methods

**Forecast target:** next-day sales for selected store-family combinations within the justified 24-month scope.

**Evaluation design:** the final 60 days are held out chronologically. Naive and Random Forest results represent rolling one-day-ahead planning where realized history becomes available each day. Holt-Winters produces a fixed 60-day path from the training cutoff. This difference is reported so the models are not treated as perfectly identical operating procedures.

### Leakage controls

- All lag and rolling features are shifted before use.
- Random splitting is not used.
- Transactions are excluded because future realized transactions would not be known at planning time.
- Calendar, holiday, and promotion-plan fields are treated as known inputs.
        """),
        code(setup),
        code("""
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import Markdown, display
from sklearn.ensemble import RandomForestRegressor
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from src.features import add_lag_features
from src.forecasting import forecast_metrics
from src.visualization import PROJECT_COLORS, save_figure, set_project_style

set_project_style()
pd.set_option("display.float_format", lambda value: f"{value:,.3f}")
subset_path = OUTPUT_DATA_DIR / "analysis_subset.csv.gz"
if not subset_path.exists():
    raise FileNotFoundError("Run Notebook 02 first to create outputs/processed_data/analysis_subset.csv.gz")
subset = pd.read_csv(subset_path, parse_dates=["date"])
scope = json.loads((OUTPUT_DATA_DIR / "analysis_scope.json").read_text())
        """),
        md("## Data\n\n### 1. Select representative forecast series"),
        code("""
series_daily = subset.groupby(["store_nbr", "family", "date"], as_index=False, observed=True).agg(
    sales=("sales", "sum"), onpromotion=("onpromotion", "sum"), is_holiday=("is_holiday", "max")
)
series_stats = series_daily.groupby(["store_nbr", "family"])["sales"].agg(mean="mean", std="std", total="sum")
series_stats["cv"] = series_stats["std"] / series_stats["mean"]
eligible = series_stats.loc[series_stats["mean"].gt(0)]

selected_series = []
selected_series.append(tuple(eligible["total"].idxmax()))
selected_series.append(tuple(eligible["cv"].idxmax()))
median_total = eligible["total"].median()
selected_series.append(tuple((eligible["total"] - median_total).abs().idxmin()))
selected_series = list(dict.fromkeys(selected_series))
display(eligible.loc[selected_series])
print("Selected series:", selected_series)
        """),
        md("## Results\n\n### 2. Fit baselines, Holt-Winters, and Random Forest"),
        code("""
validation_days = 60
feature_columns = [
    "lag_1", "lag_7", "lag_14", "lag_28", "rolling_mean_7", "rolling_mean_28",
    "day_of_week", "month", "onpromotion", "is_holiday",
]
results = []
forecast_frames = []

for store_nbr, family in selected_series:
    series = series_daily.loc[
        series_daily["store_nbr"].eq(store_nbr) & series_daily["family"].eq(family)
    ].sort_values("date").copy()
    series["day_of_week"] = series["date"].dt.dayofweek
    series["month"] = series["date"].dt.month
    featured = add_lag_features(series)
    train = featured.iloc[:-validation_days].copy()
    validation = featured.iloc[-validation_days:].copy()

    predictions = {
        "Naive (lag 1)": validation["lag_1"].to_numpy(),
        "Seasonal naive (lag 7)": validation["lag_7"].to_numpy(),
    }

    hw_model = ExponentialSmoothing(
        train["sales"], trend="add", seasonal="add", seasonal_periods=7,
        initialization_method="estimated",
    ).fit(optimized=True, use_brute=False)
    predictions["Holt-Winters"] = np.clip(hw_model.forecast(validation_days), 0, None)

    rf_train = train.dropna(subset=feature_columns)
    rf = RandomForestRegressor(
        n_estimators=200, min_samples_leaf=3, max_features=.8,
        random_state=RANDOM_SEED, n_jobs=-1,
    )
    rf.fit(rf_train[feature_columns], rf_train["sales"])
    predictions["Random Forest (rolling 1-day)"] = np.clip(
        rf.predict(validation[feature_columns]), 0, None
    )

    forecast_frame = validation[["date", "sales"]].copy()
    forecast_frame["store_nbr"] = store_nbr
    forecast_frame["family"] = family
    for model_name, predicted in predictions.items():
        forecast_frame[model_name] = np.asarray(predicted)
        metrics = forecast_metrics(validation["sales"], predicted)
        results.append({"store_nbr": store_nbr, "family": family, "model": model_name, **metrics})
    forecast_frames.append(forecast_frame)

model_results = pd.DataFrame(results)
forecasts = pd.concat(forecast_frames, ignore_index=True)
display(model_results.sort_values(["store_nbr", "family", "MAE"]))
        """),
        md("### 3. Compare average performance and inspect the representative forecast"),
        code("""
model_average = model_results.groupby("model")[["MAE", "RMSE", "RMSLE"]].mean().sort_values("MAE")
display(model_average)

representative = forecasts.loc[
    forecasts["store_nbr"].eq(selected_series[0][0])
    & forecasts["family"].eq(selected_series[0][1])
].set_index("date")
fig, ax = plt.subplots(figsize=(13, 6))
ax.plot(representative.index, representative["sales"], color="black", linewidth=2, label="Actual")
for index, model_name in enumerate(model_average.index):
    ax.plot(representative.index, representative[model_name], linewidth=1.2, alpha=.85, label=model_name, color=PROJECT_COLORS[index % len(PROJECT_COLORS)])
ax.set(
    title=f"60-day validation: Store {selected_series[0][0]} — {selected_series[0][1]}",
    xlabel="Date", ylabel="Daily sales",
)
ax.legend(ncol=2)
save_figure(fig, FIGURE_DIR, "forecast_01_validation_comparison.png")
plt.show()

fig, ax = plt.subplots(figsize=(10, 5))
model_average["MAE"].sort_values().plot(kind="barh", ax=ax, color=PROJECT_COLORS[0])
ax.set(title="Average forecast MAE across selected series", xlabel="Mean absolute error", ylabel="Model")
save_figure(fig, FIGURE_DIR, "forecast_02_model_mae.png")
plt.show()
        """),
        md("### 4. Check model consistency across demand series"),
        code("""
best_by_series = model_results.loc[model_results.groupby(["store_nbr", "family"])["MAE"].idxmin()]
display(best_by_series[["store_nbr", "family", "model", "MAE", "RMSE", "RMSLE"]])
print("Best-model counts:")
display(best_by_series["model"].value_counts())
        """),
        md("### 5. Save forecast evidence"),
        code("""
model_results.to_csv(TABLE_DIR / "forecast_model_results.csv", index=False)
model_average.reset_index().to_csv(TABLE_DIR / "forecast_model_average.csv", index=False)
best_by_series.to_csv(TABLE_DIR / "forecast_best_by_series.csv", index=False)
forecasts.to_csv(PROJECT_ROOT / "outputs" / "forecasts" / "validation_forecasts.csv", index=False)
print("Saved model metrics and validation forecasts.")
        """),
        md("## Takeaways"),
        code("""
best_model = model_average.index[0]
best_mae = model_average.iloc[0]["MAE"]
seasonal_mae = model_average.loc["Seasonal naive (lag 7)", "MAE"]
improvement = 100 * (seasonal_mae - best_mae) / seasonal_mae
display(Markdown(f'''
- **{best_model}** has the lowest average MAE (**{best_mae:,.2f}**) across the selected series.
- Relative to the weekly seasonal-naive baseline, its average MAE difference is **{improvement:,.1f}%**; this measures the chosen validation setup, not a guaranteed business improvement.
- Model winners vary by series, so operational deployment should retain a simple baseline and monitor performance by store-family rather than selecting one universal model solely from an overall average.
- The rolling Random Forest uses only lagged realized sales plus known calendar/promotion/holiday inputs; realized future transactions are excluded.
- Forecasts can support short-horizon planning, but translating error reduction into inventory or service improvements requires stock, lead-time, cost, and service-level data that this dataset does not contain.
'''))
        """),
    ],
)


write_notebook(
    "06_managerial_insights.ipynb",
    [
        md("""
# 06 — Managerial Insights

## tl;dr

This notebook consolidates the analytical evidence into a business-facing format: **Finding → Operational implication → Possible managerial action**, with explicit limitations. It is designed to support an MBA report and presentation rather than introduce new model complexity.
        """),
        md("""
## Context & Methods

The notebook reads the compact evidence tables created by Notebooks 03–05. Recommendations remain conditional: they identify where managers should differentiate planning or investigate further, not guaranteed outcomes or precise inventory policies.
        """),
        code(setup),
        code("""
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import Markdown, display

from src.visualization import PROJECT_COLORS, save_figure, set_project_style

set_project_style()
pd.set_option("display.float_format", lambda value: f"{value:,.3f}")

required_tables = [
    "store_operations_summary.csv", "family_operations_segments.csv",
    "promotion_operations_summary.csv", "peak_weekdays.csv", "peak_months.csv",
    "forecast_model_average.csv",
]
missing = [name for name in required_tables if not (TABLE_DIR / name).exists()]
if missing:
    raise FileNotFoundError(f"Run Notebooks 03–05 first. Missing tables: {missing}")

stores = pd.read_csv(TABLE_DIR / "store_operations_summary.csv")
families = pd.read_csv(TABLE_DIR / "family_operations_segments.csv")
promotions = pd.read_csv(TABLE_DIR / "promotion_operations_summary.csv")
weekdays = pd.read_csv(TABLE_DIR / "peak_weekdays.csv")
months = pd.read_csv(TABLE_DIR / "peak_months.csv")
models = pd.read_csv(TABLE_DIR / "forecast_model_average.csv")
        """),
        md("## Results\n\n### 1. Executive evidence snapshot"),
        code("""
top_store = stores.nlargest(1, "average_daily_sales").iloc[0]
volatile_store = stores.nlargest(1, "demand_cv").iloc[0]
top_family = families.nlargest(1, "total_sales").iloc[0]
volatile_family = families.nlargest(1, "cv").iloc[0]
peak_day = weekdays.nlargest(1, "mean").iloc[0]
peak_month = months.nlargest(1, "mean").iloc[0]
best_model = models.nsmallest(1, "MAE").iloc[0]

snapshot = pd.DataFrame(
    [
        ("Highest average-demand store", f"Store {int(top_store.store_nbr)}", top_store.average_daily_sales),
        ("Most variable store", f"Store {int(volatile_store.store_nbr)}", volatile_store.demand_cv),
        ("Largest product family", top_family.family, top_family.total_sales),
        ("Most variable family", volatile_family.family, volatile_family.cv),
        ("Peak average weekday", peak_day.weekday, peak_day["mean"]),
        ("Peak average month", f"Month {int(peak_month.month)}", peak_month["mean"]),
        ("Lowest average-MAE model", best_model.model, best_model.MAE),
    ],
    columns=["indicator", "result", "value"],
)
display(snapshot)
        """),
        md("### 2. Finding → implication → action register"),
        code("""
high_stable = families.loc[families["segment"].eq("High demand / Stable")].nlargest(3, "total_sales")["family"].tolist()
high_volatile = families.loc[families["segment"].eq("High demand / Volatile")].nlargest(3, "total_sales")["family"].tolist()
top_promo = promotions.loc[promotions["promoted_observations"].ge(100)].nlargest(3, "observed_ratio")["family"].tolist()

insights = pd.DataFrame(
    [
        {
            "Finding": f"High-demand/stable families include {', '.join(high_stable) or 'none under the median rule'}.",
            "Operational implication": "Large, relatively predictable flows can anchor routine capacity and replenishment planning.",
            "Possible managerial action": "Use regular review cycles and supplier schedules, then monitor exceptions rather than treating every day as equally uncertain.",
            "Limitation": "Inventory policy still requires lead times, stock, costs, and service targets.",
        },
        {
            "Finding": f"High-demand/volatile families include {', '.join(high_volatile) or 'none under the median rule'}.",
            "Operational implication": "These categories combine commercial importance with planning uncertainty.",
            "Possible managerial action": "Prioritize shorter planning cycles, scenario ranges, and closer supplier coordination for these families.",
            "Limitation": "CV is a relative historical measure and does not identify the cause of volatility.",
        },
        {
            "Finding": f"Store {int(volatile_store.store_nbr)} has the highest daily-demand CV ({volatile_store.demand_cv:.3f}).",
            "Operational implication": "Uniform store rules may leave volatile locations under- or over-prepared.",
            "Possible managerial action": "Use store-specific staffing and receiving flexibility, and investigate local calendar or assortment drivers.",
            "Limitation": "Sales mix and opening history may explain part of the difference.",
        },
        {
            "Finding": f"Average network demand peaks on {peak_day.weekday} and in month {int(peak_month.month)}.",
            "Operational implication": "Recurring peaks can strain labor, shelf replenishment, checkout, receiving, and supplier capacity.",
            "Possible managerial action": "Review rosters, delivery windows, and replenishment frequency ahead of these recurring periods.",
            "Limitation": "Averages can mask store- and family-specific peak timing.",
        },
        {
            "Finding": f"Strong promotion-associated ratios appear for {', '.join(top_promo)} among adequately represented families.",
            "Operational implication": "Promotion response appears heterogeneous and may create category-specific capacity pressure.",
            "Possible managerial action": "Coordinate promotions with replenishment and staffing; test incremental lift with stronger causal designs.",
            "Limitation": "The descriptive ratio is not causal and may reflect promotion targeting or seasonality.",
        },
        {
            "Finding": f"{best_model.model} has the lowest average validation MAE ({best_model.MAE:,.2f}) for the selected series.",
            "Operational implication": "Forecasting can improve short-horizon visibility for selected demand series, but value varies by series.",
            "Possible managerial action": "Pilot forecasts alongside a seasonal-naive baseline and monitor error by store-family before wider use.",
            "Limitation": "Validation covers selected series and one historical period; it does not prove inventory savings.",
        },
    ]
)
display(insights)
insights.to_csv(TABLE_DIR / "managerial_insights.csv", index=False)
        """),
        md("### 3. Portfolio priorities for presentation"),
        code("""
segment_counts = families["segment"].value_counts().reindex(
    ["High demand / Stable", "High demand / Volatile", "Low demand / Stable", "Low demand / Volatile"], fill_value=0
)
fig, ax = plt.subplots(figsize=(10, 5))
segment_counts.plot(kind="barh", ax=ax, color=PROJECT_COLORS)
ax.set(title="Product-family portfolio by demand and variability", xlabel="Number of families", ylabel="Operational segment")
save_figure(fig, FIGURE_DIR, "managerial_01_portfolio_segments.png")
plt.show()
        """),
        md("## Takeaways"),
        code("""
display(Markdown(f'''
1. **Differentiate the portfolio.** Stable high-demand families support standardized routines; volatile high-demand families merit closer review and flexibility.
2. **Plan locally.** Store {int(volatile_store.store_nbr)} illustrates why a single network-wide variability assumption is insufficient.
3. **Prepare for recurring peaks.** {peak_day.weekday} and month {int(peak_month.month)} are network-level signals for labor, receiving, replenishment, and supplier coordination reviews.
4. **Treat promotion evidence carefully.** Use observed differences to prioritize tests and operational coordination, not to claim causal lift.
5. **Use forecasting as support.** Retain transparent baselines, monitor by series, and connect forecasts to actual planning decisions before expanding complexity.
6. **Request missing operational data.** Stock levels, stockouts, lead times, costs, margins, order quantities, and service targets are needed for inventory-policy or financial-impact claims.
'''))
        """),
    ],
)


print(f"Generated six notebooks in {NOTEBOOK_DIR}")
