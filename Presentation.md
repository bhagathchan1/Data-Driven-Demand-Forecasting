# PPTX Generation Brief

## How to use this file

1. Upload this file and the PNG files from `reports/figures/` to the presentation-generating LLM.
2. Ask the LLM to follow the presentation instructions and slide specifications below.
3. Keep all stated numbers, qualifications, and limitations unchanged.
4. Replace the bracketed student details on Slide 1 before submitting the deck.
5. Review the generated PPTX to confirm that chart labels remain readable and that no unsupported claims were added.

---

## Copy-ready instruction for the presentation-generating LLM

Create an editable 16:9 PowerPoint presentation from the slide specifications in this document.

Audience: MBA faculty and classmates evaluating an Operations Management project supported by Data Science.

Purpose: explain how historical sales and operational factors can support grocery retail demand planning. The presentation must remain business-oriented. Forecasting is one decision-support component, not the entire project.

Use the supplied PNG charts as evidence. Do not recreate their numbers or invent additional results. Keep the titles, numerical values, units, caveats, and managerial meaning provided below. If a chart file is unavailable, create a simple editable chart only from the data explicitly supplied in this document.

Presentation requirements:

- Create exactly 18 slides, including the title and closing slides.
- Use a professional academic style with a white or very light background, dark navy text, and restrained teal or orange accents.
- Use one clean sans-serif font family throughout.
- Use at least 32 pt for slide titles and 18 pt for body text.
- Prefer one evidence-led composition per slide. Avoid dashboards, dense card grids, decorative icons, and stock photographs.
- Use charts for quantitative findings and concise text for interpretation.
- Keep source notes and limitations visible in small text where specified.
- Add the supplied speaker notes to each slide.
- Do not add a confusion matrix. This project predicts continuous daily sales, so regression metrics are appropriate.
- Do not describe associations as causal effects.
- Do not claim inventory optimization. The data does not contain stock-on-hand, stockouts, lead times, costs, margins, or service targets.
- Refer to sales as `mixed units` when combining product families because the data is neither revenue nor a single physical unit.
- Preserve editability for titles, text, tables, and any charts created from supplied values.

---

## Slide specifications

### Slide 1: Title

**Title:** Data-Driven Demand Analysis and Forecasting for Grocery Retail Operations

**Subtitle:** An Operations Management project supported by Data Science

**Details:**

- MBA Year 1 Project
- Student: [Name]
- Institution: [Institution]
- Date: [Presentation Date]

**Visual direction:** Minimal title slide. Use a subtle grocery retail or time-series visual motif. Do not place analytical findings on this slide.

**Speaker notes:**

This project examines how retail sales history and operational context can support demand planning. The emphasis is on business interpretation and operational decisions rather than building a model leaderboard.

---

### Slide 2: Executive summary

**Title:** Demand concentration and calendar peaks require differentiated planning

**On-slide content:**

- Four product families account for **72.7%** of observed sales.
- Average network sales are highest on **Sunday at 825.2k mixed units**.
- **13 families** have high demand with relatively stable daily patterns, while **4** combine high demand with high variability.
- Holiday store-days average **19.1% higher observed sales** than non-holiday store-days.
- The best average forecasting result comes from a rolling one-day Random Forest with **MAE 414.4**, but the winning model varies by series.

**Bottom-line message:** One network-wide planning rule would ignore meaningful differences across categories, stores, and operating periods.

**Visual direction:** Use one strong text hierarchy with the 72.7%, 825.2k, 19.1%, and 414.4 figures emphasized. Avoid a grid of KPI cards.

**Speaker notes:**

The analysis supports differentiated planning. Stable high-volume categories can use regular routines. Volatile important categories, weekend peaks, holidays, promotion periods, and high-variability stores need shorter review cycles and more operating flexibility.

---

### Slide 3: Business question and objectives

**Title:** Business question and project objectives

**Main question:**

> How can historical sales and operational factors be analyzed to understand demand patterns and support better retail planning decisions?

**Objectives:**

1. Understand historical retail demand patterns.
2. Identify factors associated with changes in sales.
3. Examine differences across stores and product families.
4. Assess the operational relevance of promotions, holidays, and demand variability.
5. Develop a suitable forecast for selected demand series.
6. Translate the evidence into practical planning recommendations.

**Speaker notes:**

The question remains deliberately broad so the project follows the evidence in the data. The project does not set arbitrary improvement targets and does not claim direct inventory optimization.

---

### Slide 4: Dataset and analytical grain

**Title:** Dataset coverage and unit of analysis

**On-slide table:**

| Dataset | Rows | Role |
|---|---:|---|
| Historical sales | 3,000,888 | Sales and promotion observations |
| Test horizon | 28,512 | Competition forecast period |
| Stores | 54 | Geography, type, and cluster |
| Transactions | 83,488 | Daily store-traffic proxy |
| Holidays and events | 350 | National, regional, and local events |
| Oil prices | 1,218 | Exploratory economic context |

**Supporting facts:**

- Training period: **1 January 2013 to 15 August 2017**
- Coverage: **54 stores, 33 families, and 1,684 observed dates**
- Core grain: **one date × store × product-family observation**
- Key validation: 1,684 × 54 × 33 = **3,000,888 unique rows**

**Speaker notes:**

The files operate at different levels. Store attributes are static, transactions are daily by store, oil is daily, and holidays can have overlapping geographic scopes. Join validation is essential because an incorrect merge could duplicate sales or apply local events to every store.

---

### Slide 5: Analysis workflow

**Title:** Business-led analytical workflow

**On-slide process:**

Business problem → data understanding → cleaning and validated joins → focused EDA → operations analysis → forecasting support → managerial recommendations

**Method details:**

- Full dataset used for network-level patterns.
- Transparent subset used for detailed analysis and forecasting.
- Descriptive associations separated from causal conclusions.
- Chronological validation used for forecasts.
- Results translated into operating implications and possible actions.

**Visual direction:** Present the workflow as one horizontal process with simple labels. Keep forecasting as one stage rather than the dominant stage.

**Speaker notes:**

The workflow starts with a business question and ends with operating decisions. Data quality checks protect the analysis, and forecasts are evaluated by whether they add useful planning information beyond simple baselines.

---

### Slide 6: Data quality and preparation

**Title:** Data quality decisions preserve operational meaning

**On-slide content:**

- No exact duplicates, duplicate sales keys, or negative sales values were found.
- **939,130 rows, or 31.30%, contain zero sales.** These observations were retained because they may reflect genuine low demand, closures, or store lifecycle.
- Oil has **43 missing values**. Values were filled across a daily time index and flagged.
- Transactions are missing for **7,448 of 90,936 store-dates, or 8.19%**. Missing records remain missing rather than becoming zero traffic.
- Holiday data has 350 rows across 312 dates because several dates contain multiple events or geographic scopes.
- National, regional, and local holidays were matched to the relevant stores.

**Footer:** Outliers were investigated and retained. Retail spikes may represent promotions, holidays, special events, or disruptions.

**Speaker notes:**

Blind deletion would remove operationally meaningful variation. The preparation process keeps raw values intact, adds transparent flags, and validates every merge to preserve all 3,000,888 sales rows.

---

### Slide 7: Analytical scope

**Title:** Detailed analysis uses a transparent two-year subset

**On-slide content:**

- Period: **16 August 2015 to 15 August 2017**
- Stores: **44, 45, 17, 32, and 25**
- Families: **Grocery I, Beverages, Produce, Cleaning, and Frozen Foods**
- Eligibility: at least **90% transaction coverage** and **90% active-sales coverage**

**Selection logic:**

- Two high-volume stores
- One near-median store
- One low-volume store
- One relatively volatile mature store
- Five operationally important families with different scale and variability patterns

**Key reason:** Lifecycle coverage prevents late-opening stores from appearing artificially volatile because of pre-opening zero rows.

**Speaker notes:**

The full dataset still supports high-level findings. The subset makes detailed comparisons manageable without choosing stores or families arbitrarily.

---

### Slide 8: Overall demand trend

**Title:** Average daily network sales more than doubled from 2013 to 2016

**Primary visual:** `reports/figures/eda_01_total_sales_trend.png`

**On-slide evidence:**

- Average daily sales increased from approximately **385.8k mixed units in 2013** to **790.8k in 2016**.
- Partial-year 2017 averages approximately **855.6k**, based on data through 15 August.
- The 28-day moving average shows growth, recurring weekly movement, peaks, and several near-zero network dates.

**Operational implication:** Historical capacity and supplier requirements increased, but store openings and assortment changes may explain part of the trend.

**Speaker notes:**

The trend represents observed network sales, not confirmed same-store organic growth. A capacity decision should separate store-network expansion from demand growth before locking in long-term commitments.

---

### Slide 9: Calendar demand patterns

**Title:** Weekends and December create recurring demand peaks

**Primary visual:** `reports/figures/eda_02_calendar_patterns.png`

**On-slide evidence:**

- Sunday: **825.2k average daily mixed units**
- Saturday: **772.2k**
- Thursday: approximately **505.3k**, the lowest weekday average
- December: **808.6k average daily mixed units**, the highest monthly average

**Operational implication:** Weekend and year-end plans should review staffing, checkout coverage, delivery timing, receiving capacity, and shelf replenishment.

**Speaker notes:**

These are network averages. Store and family patterns should refine the final operating plan. The evidence supports advance reviews before predictable peaks, not a single universal capacity multiplier.

---

### Slide 10: Store performance

**Title:** Store scale and variability differ across the network

**Primary visual:** `reports/figures/eda_03_store_performance.png`

**Secondary visual if space permits:** `reports/figures/operations_02_store_profiles.png`

**On-slide evidence:**

- Store 44 has the highest observed sales at approximately **62.1 million mixed units**.
- Stores 45, 47, 3, and 49 complete the five highest-volume stores.
- Among mature stores with adequate coverage, Store 25 has the highest daily-demand CV at **0.702**.
- Seven stores fail the 90% lifecycle coverage rule and remain separate from mature-store variability comparisons.

**Operational implication:** Labor, receiving flexibility, and replenishment review thresholds should reflect store scale and mature-store variability.

**Speaker notes:**

A smaller or newer store should not automatically be labelled underperforming. Store rankings need context from opening history, coverage, format, and local demand.

---

### Slide 11: Product-family portfolio

**Title:** Four families contribute 72.7% of observed sales

**Primary visual:** `reports/figures/eda_04_family_importance_variability.png`

**On-slide table:**

| Family | Sales share | Daily-demand CV | Planning interpretation |
|---|---:|---:|---|
| Grocery I | 31.99% | 0.303 | Very high volume and relatively stable |
| Beverages | 20.21% | 0.490 | High volume with moderate variability |
| Produce | 11.43% | 0.849 | High volume and volatile |
| Cleaning | 9.08% | 0.263 | High volume and relatively stable |
| Dairy | 6.01% | 0.358 | Important and comparatively stable |

**Operational implication:** Volume and uncertainty require different responses. Grocery I and Cleaning can support regular routines. Produce requires closer monitoring and more flexible planning.

**Speaker notes:**

The coefficient of variation equals standard deviation divided by mean demand. It supports comparison of relative variability across families with different sales levels.

---

### Slide 12: Promotions and holidays

**Title:** Promotion and holiday associations vary materially

**Primary visual:** `reports/figures/eda_06_promotion_association.png`

**On-slide evidence:**

Promoted versus non-promoted mean-sales ratios among important families:

- Produce: **3.08**
- Home Care: **3.04**
- Beverages: **2.49**
- Dairy: **1.95**
- Grocery I: **1.62**
- Cleaning: **1.43**

Holiday store-days average **13.8k mixed units**, compared with **11.6k** on normal store-days. The descriptive difference is **19.1%**.

**Operational implication:** Promotion calendars and holiday plans should be coordinated with supply availability, shelf capacity, receiving, and staffing.

**Required caveat:** These results show association, not causal lift. Timing, targeting, weekday, month, and store differences may influence the comparison.

**Speaker notes:**

The ratios identify where operating pressure may be stronger during promotions. They do not establish incremental sales caused by the promotion. A causal estimate would require a stronger comparison design.

---

### Slide 13: Transactions and oil context

**Title:** Transactions support traffic planning, while oil remains exploratory

**Primary visual:** `reports/figures/eda_07_transactions.png`

**Secondary visual:** `reports/figures/eda_08_oil_context.png`

**On-slide evidence:**

- Store-day sales and transactions have a **Pearson correlation of 0.837** where both are available.
- Transactions are a useful traffic proxy for staffing and checkout planning.
- Sales divided by transactions is only a mixed-unit basket proxy, not revenue per transaction.
- Monthly sales and oil prices have a contemporaneous correlation of approximately **-0.788**.

**Required caveat:** The oil relationship may reflect time trends, store openings, inflation, and omitted variables. It should not drive planning without further time-aware analysis.

**Speaker notes:**

The transaction relationship has a direct operational interpretation because customer traffic affects workload. The oil correlation is included as exploratory context and demonstrates why correlation alone does not establish a business driver.

---

### Slide 14: Operations segmentation

**Title:** Demand level and variability define four planning postures

**Primary visual:** `reports/figures/operations_01_family_segments.png`

**On-slide table:**

| Segment | Number of families | Planning posture |
|---|---:|---|
| High demand / Stable | 13 | Standard routines with exception monitoring |
| High demand / Volatile | 4 | Shorter review cycles and flexible capacity |
| Low demand / Stable | 3 | Lower-frequency review where service risk permits |
| Low demand / Volatile | 13 | Selective monitoring and cautious interpretation of percentage changes |

**Management example:** Produce belongs to the high-demand and volatile group. It deserves more attention than a low-demand volatile family because both service risk and operating workload are greater.

**Speaker notes:**

The segmentation uses median daily demand and median CV as transparent portfolio cutoffs. It is a decision framework for this dataset, not a universal retail classification.

---

### Slide 15: Forecast design and evaluation

**Title:** Forecasting tests whether analytical support improves on simple baselines

**On-slide content:**

**Target:** Daily sales for three representative store-family series

**Validation:** Final 60 observations held out chronologically

**Models:**

- Naive forecast using the previous day
- Seasonal naive forecast using the previous week
- Holt-Winters exponential smoothing
- Random Forest using shifted sales lags, rolling averages, calendar fields, promotions, and holiday indicators

**Leakage controls:**

- Lag and rolling features shifted before use
- No random train-test split
- Future realized transactions excluded

**Why no confusion matrix:** A confusion matrix evaluates categorical predictions. Daily sales is continuous, so the correct measures are **MAE, RMSE, RMSLE, per-series comparison, and actual-versus-forecast plots**.

**Speaker notes:**

MAE provides an intuitive average error in sales units. RMSE gives more weight to large misses. RMSLE focuses more on proportional error and reduces domination by high-volume series.

---

### Slide 16: Forecast results

**Title:** Random Forest leads on average, but one model does not win every series

**Primary visual:** `reports/figures/forecast_01_validation_comparison.png`

**Secondary visual if space permits:** `reports/figures/forecast_02_model_mae.png`

**On-slide table:**

| Model | Average MAE | Average RMSE | Average RMSLE |
|---|---:|---:|---:|
| Random Forest, rolling one-day | **414.41** | **592.87** | **0.258** |
| Holt-Winters | 647.09 | 789.75 | 0.286 |
| Seasonal naive, lag 7 | 718.64 | 945.90 | 0.315 |
| Naive, lag 1 | 910.54 | 1,104.41 | 0.334 |

**Key result:** Random Forest average MAE is **42.3% lower** than the weekly seasonal-naive baseline.

**Series-level winners:**

- Store 45, Grocery I: Random Forest, MAE **982.09**
- Store 32, Grocery I: Random Forest, MAE **252.30**
- Store 32, Frozen Foods: Holt-Winters, MAE **7.51**

**Required caveat:** The Random Forest uses rolling one-day realized history. Holt-Winters produces a fixed 60-day path from the cutoff. The update procedures are useful operational alternatives but are not perfectly identical experiments.

**Speaker notes:**

Average MAE can be dominated by high-volume series, which is why proportional error and individual-series winners also matter. The correct operational conclusion is to retain a transparent seasonal baseline and monitor model performance by store-family series.

---

### Slide 17: Managerial recommendations

**Title:** Evidence supports differentiated planning policies

**On-slide table:**

| Finding | Operational implication | Possible action |
|---|---|---|
| Grocery I and Cleaning have high volume with relative stability | Large flows are comparatively predictable | Use regular supplier and review cycles with exception monitoring |
| Produce combines high demand and high variability | Fixed planning cycles may react slowly | Use shorter review cycles and coordinate more closely with suppliers |
| Weekends and December have higher average demand | Recurring peaks can strain stores | Review rosters, delivery windows, and replenishment frequency before peak periods |
| Mature stores differ in variability | A single store rule can overprepare or underprepare locations | Set store-specific planning tolerances and treat new stores separately |
| Promotion association differs by family | Promotion workload is category-specific | Link campaign calendars with supply, shelf-space, and labor reviews |
| Forecast winners vary by series | A universal model may be fragile | Compare each model with the seasonal baseline and monitor errors by series |

**Speaker notes:**

These actions translate observed patterns into planning routines. They are intentionally practical but not over-precise because the dataset lacks operational constraints such as labor productivity, shelf capacity, lead times, and supplier limits.

---

### Slide 18: Conclusion and limitations

**Title:** Data science supports better operating choices when uncertainty stays visible

**Conclusion:**

- Prioritize high-volume categories without assuming equal predictability.
- Prepare for recurring weekend, holiday, promotion, and year-end pressure.
- Separate mature-store comparisons from opening and incomplete-history effects.
- Use forecasts alongside transparent baselines and monitor results by series.

**Important limitations:**

- Sales may be constrained by stockouts or closures and are not unconstrained demand.
- Mixed product units are not revenue, margin, or a common physical quantity.
- Promotion, holiday, transaction, and oil analyses are observational.
- Forecast testing covers three series and one 60-day holdout.
- Inventory optimization requires stock, lead-time, cost, margin, and service-level data that is unavailable here.

**Closing statement:** The project connects trustworthy evidence to demand planning, staffing, capacity, promotion coordination, and replenishment review without overstating what the data can prove.

**Speaker notes:**

The main contribution is not one best model. It is a structured way to distinguish scale, variability, calendar peaks, store lifecycle, and forecast uncertainty so managers can apply different planning responses where they are justified.

---

## Optional appendix material

Use these only if the presentation format allows appendix slides beyond the required 18 slides.

### Appendix A: Metric definitions

| Metric | Definition | Managerial interpretation |
|---|---|---|
| Coefficient of variation | Standard deviation divided by mean demand | Relative variability across differently scaled series |
| MAE | Mean absolute error | Average forecast miss in sales units |
| RMSE | Square root of mean squared error | Gives more weight to large forecast misses |
| RMSLE | Root mean squared logarithmic error | Emphasizes proportional error |
| Pearson correlation | Linear association from -1 to +1 | Descriptive association, not proof of causation |

### Appendix B: Reproducibility

- Dataset: Kaggle Store Sales - Time Series Forecasting
- Executed notebooks: `notebooks/01_data_understanding.ipynb` to `notebooks/06_managerial_insights.ipynb`
- Reusable code: `src/`
- Evidence tables: `reports/tables/`
- Figures: `reports/figures/`
- Full written analysis: `reports/final_report.md`

### Appendix C: Suggested viva questions

**Why did you retain zero sales?**

Zeros can represent genuine demand conditions, closures, or store lifecycle. Removing them without operational evidence could bias the analysis.

**Why did you not use a confusion matrix?**

The target is continuous daily sales. Confusion matrices apply to categorical predictions. MAE, RMSE, RMSLE, and forecast plots preserve the size and timing of errors.

**Why can promotion ratios not be called promotion lift?**

Promotions are not randomly assigned. Timing, product choice, store selection, seasonality, and expected demand may influence both promotion decisions and sales.

**Why is oil treated cautiously despite a strong correlation?**

Both series trend over time and may respond to omitted variables. A contemporaneous correlation does not prove that oil prices drive grocery demand.

**Why use a subset?**

The subset enables interpretable store-family analysis and forecasting. Transparent eligibility and selection rules reduce arbitrary choices while the full panel remains available for network-level findings.

**Can the project calculate optimal safety stock?**

No. That requires inventory positions, stockouts, lead times, service targets, costs, and supplier constraints, none of which are available in the competition data.

---

## Final quality checklist for the generated PPTX

- Exactly 18 main slides are present.
- Every numerical claim matches this document.
- Charts use the supplied files and remain readable.
- Slide titles state the actual topic or supported finding.
- The deck explains the business relevance of each analytical result.
- Association is not described as causation.
- Sales are labelled as mixed units where families are combined.
- No confusion matrix appears.
- No claim of inventory optimization appears.
- Forecasting remains a supporting part of the Operations Management story.
- Speaker notes contain the supplied explanations.
- Student details are completed before submission.
