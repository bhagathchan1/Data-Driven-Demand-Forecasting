# Project Summary and Detailed Analytical Walkthrough

## Project purpose

This MBA live project uses the Kaggle **Store Sales – Time Series Forecasting** data to examine how historical sales and operational context can support grocery-retail planning. The project is deliberately organized as an Operations Management study supported by data science:

```text
Business question → data audit → cleaning and validated integration →
demand-pattern analysis → operations diagnosis → forecasting support →
managerial actions and limitations
```

The central business question is:

> How can historical sales and operational factors be analyzed to understand demand patterns and support better retail planning decisions?

The analysis does not claim inventory optimization because the dataset has no stock-on-hand, stockout, order, lead-time, cost, margin, or service-level data.

## Data used

All seven files in the locally downloaded competition archive were verified before analysis.

| File | Rows | Role |
|---|---:|---|
| `train.csv` | 3,000,888 | Daily sales and promotions at date × store × family grain |
| `test.csv` | 28,512 | Competition forecast horizon |
| `stores.csv` | 54 | City, state, type, and cluster for each store |
| `transactions.csv` | 83,488 | Daily transactions by store |
| `holidays_events.csv` | 350 | National, regional, and local events |
| `oil.csv` | 1,218 | WTI oil-price context |
| `sample_submission.csv` | 28,512 | Competition output structure |

Raw files remain unchanged in `data/raw/` and are excluded from Git.

## Step-by-step workflow

### Step 1 — Repository and environment setup

**What was done**

- Created the `data`, `notebooks`, `src`, `reports`, and `outputs` structure.
- Added a `.gitignore` that excludes raw Kaggle data, generated processed datasets, caches, and local environments.
- Added a minimal `requirements.txt` containing only libraries used by the project.
- Added `data/README.md` with Kaggle download and placement instructions.
- Centralized reusable loading, preparation, features, EDA, visualization, and forecasting logic in `src/`.

**Why it matters**

The analysis is reproducible, source data is protected, and business logic is not duplicated across notebooks.

### Step 2 — Data understanding

**Notebook:** `notebooks/01_data_understanding.ipynb`

**Checks performed**

- Verified file availability and size.
- Printed shapes, columns, data types, date ranges, and memory usage.
- Identified candidate keys and dataset grains.
- Checked exact duplicates, duplicate candidate keys, invalid dates, missing values, and orphan store keys.
- Profiled numeric and categorical fields.
- Created a compact data dictionary.

**Validated result**

- The training data covers 1 January 2013 through 15 August 2017.
- It contains 1,684 dates, 54 stores, and 33 product families.
- `3,000,888 = 1,684 × 54 × 33`, so the core sales panel is structurally complete at date × store × family grain.
- No duplicate core keys or negative sales were found.
- 939,130 rows, or 31.30%, have zero sales and were retained for investigation.

### Step 3 — Cleaning and validated integration

**Notebook:** `notebooks/02_data_cleaning.ipynb`

**What was checked**

- Missing values, duplicate rows, invalid types and dates, negative and zero sales, promotion extremes, transaction coverage, holiday duplicates, and robust sales extremes.
- Extreme observations were profiled by family rather than deleted.

**Transformations**

- Added year, month, quarter, ISO week, weekday, day-of-month, and weekend fields.
- Added a log-scaled promotion-intensity field.
- Built a daily oil series with forward filling and an explicit imputation flag.
- Retained missing transactions as missing instead of converting them to zero.
- Matched non-transferred holidays by scope: national to all stores, regional to state, and local to city.

**Validation after integration**

- Every merge used cardinality validation.
- Row count remained 3,000,888.
- The date × store × family key remained unique.
- No sales row lost its store attributes.

**Scope reduction**

The full panel remains the basis for network-level analysis. Detailed analysis uses:

- Stores 44, 45, 17, 32, and 25;
- Grocery I, Beverages, Produce, Cleaning, and Frozen Foods;
- 16 August 2015 through 15 August 2017.

Stores were selected only after applying transaction and active-sales coverage checks, then choosing high-, median-, low-volume, and relatively volatile mature stores. Families include the four largest by sales plus a high-variability family among the top 15 by volume.

### Step 4 — Core exploratory demand analysis

**Notebook:** `notebooks/03_exploratory_data_analysis.ipynb`

The notebook answers a defined question with each chart:

1. **Network trend:** daily sales and a 28-day rolling average.
2. **Calendar pattern:** yearly daily averages, month seasonality, and weekday differences.
3. **Store performance:** store ranking, store type, cluster, geography, variability, and transaction coverage.
4. **Family performance:** contribution, daily variability, historical growth, and high/low volume comparison.
5. **Store–family mix:** a heatmap for the justified detailed subset.
6. **Promotions:** promoted/non-promoted mean-sales ratios by family and store, reported as associations rather than causal lift.
7. **Holidays:** store-scope-aware holiday/normal comparisons and major event dates.
8. **Transactions:** store-day traffic versus sales and a mixed-unit sales-per-transaction proxy.
9. **Oil:** exploratory monthly co-movement with explicit non-causal interpretation.

### Step 5 — Advanced EDA for operational interpretation

Four additional analyses deepen the MBA story without changing the causal limits:

1. **Demand intermittency:** 1,782 store–family time series are classified with ADI and CV². Results: 630 Smooth, 593 Intermittent, 324 Lumpy, and 235 Erratic series. Fifty-three all-zero series are retained and displayed separately at the plot boundary. This is a screening tool for forecast evaluation and review cadence—not a safety-stock calculation.
2. **Semi-month boundary proxy:** average network sales are 4.52% higher in a window around the 15th and month-end than on other dates. This is descriptive and does not control for weekday, holidays, trend, or promotion mix.
3. **April 2016 structural-shock window:** equal 30-day pre/post average daily sales are compared. Manabí is 64.91% higher in the post window, while Santa Elena is 38.77% lower. These are temporal associations, not causal estimates.
4. **Cross-family co-movement:** correlations use daily log-sales changes instead of raw levels and remove the daily cross-family mean change. This reduces shared growth and network-wide movement; remaining correlations still do not establish product complementarity.

### Step 6 — Operations analysis

**Notebook:** `notebooks/04_operations_analysis.ipynb`

**Measures**

- Mean daily demand, standard deviation, and coefficient of variation.
- Store daily sales, transactions, promotion-active days, coverage, and seasonal sensitivity.
- Family promotion association and recurring weekday/month peaks.

**Segmentation**

Families are placed into four relative portfolio groups using median demand and median CV:

- High demand / Stable: 13
- High demand / Volatile: 4
- Low demand / Stable: 3
- Low demand / Volatile: 13

The segmentation supports differentiated review cadence and capacity attention. It does not prescribe reorder points or buffers.

### Step 7 — Forecasting as decision support

**Notebook:** `notebooks/05_forecasting.ipynb`

**Target and design**

- Daily sales for three representative store–family series.
- Chronological 60-day validation; no random split.
- Leakage-safe lags at 1, 7, 14, and 28 days and shifted rolling means at 7 and 28 days.
- Future realized transactions excluded.

**Models compared**

- One-day naive
- Seven-day seasonal naive
- Holt-Winters exponential smoothing
- Random Forest with rolling one-day updates

**Average validation results**

| Model | MAE | RMSE | RMSLE |
|---|---:|---:|---:|
| Random Forest, rolling one-day | 414.41 | 592.87 | 0.258 |
| Holt-Winters | 647.09 | 789.75 | 0.286 |
| Seasonal naive, lag 7 | 718.64 | 945.90 | 0.315 |
| Naive, lag 1 | 910.54 | 1,104.41 | 0.334 |

Random Forest performs best on average, but Holt-Winters wins for Store 32–Frozen Foods. The forecast procedures do not have identical update schedules, so results are operational comparisons rather than a universal model ranking.

### Step 8 — Managerial synthesis

**Notebook:** `notebooks/06_managerial_insights.ipynb`

Each recommendation follows:

```text
Finding → Operational implication → Possible managerial action → Limitation
```

The main actions are to differentiate family review cadence, tailor store planning tolerances, prepare labor and receiving for weekend/December peaks, coordinate promotions with capacity, and pilot forecasts alongside a seasonal-naive benchmark.

### Step 9 — Reporting and presentation assets

- `reports/findings.md`: running evidence register.
- `reports/final_report.md`: business-oriented MBA report.
- `Presentation.md`: copy-ready 18-slide presentation brief with speaker notes.
- `DATA_SCIENCE_CANVAS.md`: one-page project canvas and decision matrix.
- `reports/figures/`: presentation-ready analytical figures.
- `reports/tables/`: compact evidence tables supporting reported values.

## Key findings

- Grocery I, Beverages, Produce, and Cleaning contribute approximately 72.7% of observed family-level sales.
- Store 44 has the highest total observed sales at approximately 62.1 million mixed units.
- Average demand is highest on Sunday (825.2k) and Saturday (772.2k); December is the highest month (808.6k average daily sales).
- Transactions and sales have a 0.837 store-day correlation where transactions are available.
- Holiday store-days average 19.1% more sales than non-holiday store-days, but the comparison is observational.
- Promotion associations vary materially by family and store.
- Forecast usefulness varies by demand series; no single method wins everywhere.

## Quality controls completed

- Raw files preserved and excluded from Git.
- All six notebooks executed top-to-bottom with no cell errors.
- Core grain, row counts, and join cardinalities validated.
- Chronological model validation and shifted features used to prevent leakage.
- Presentation figures saved at high resolution.
- Reported numerical claims linked to notebook outputs and evidence tables.
- Causal, inventory-optimization, and financial-benefit claims excluded where unsupported.

## Limitations and additional data needed

The next level of operational decision-making would require stock-on-hand, stockouts, order history, supplier lead times, costs, margins, delivery capacity, labor productivity, and service-level targets. These would enable service-level design, reorder-point calculation, safety-stock analysis, and financial impact assessment.
