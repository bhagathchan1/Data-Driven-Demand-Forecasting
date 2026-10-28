# Running Findings

Results are descriptive unless a stronger design supports causal interpretation.

## Phase 1 — Data understanding

### Complete core sales panel

**Finding:** The training data contains one row for every observed date-store-family combination over its date range.

**Evidence:** 3,000,888 rows = 1,684 dates × 54 stores × 33 product families; the `id` and (`date`, `store_nbr`, `family`) keys are unique, with no exact duplicate rows.

**Operational implication:** The core sales panel supports consistent cross-store and cross-family comparisons without reconstructing missing grid rows.

**Potential action:** Preserve this grain through cleaning and explicitly validate row counts after every join.

**Limitations:** A present row with zero sales does not establish whether true demand was zero, the store was closed, or a stockout suppressed observed sales.

### Zero-sales observations require contextual review

**Finding:** Zero sales are common in the training panel.

**Evidence:** 939,130 of 3,000,888 training rows (31.30%) report zero sales; no negative sales were observed.

**Operational implication:** Treating every zero as ordinary low demand could distort variability and forecast evaluation.

**Potential action:** Examine zeros by store, family, date, transactions, holidays, and known closures before choosing cleaning rules.

**Limitations:** The dataset has no direct stock-on-hand or store-open indicator.

### Context tables need careful time and scope handling

**Finding:** Oil values and transaction coverage are incomplete relative to the full daily sales panel, while holiday dates can legitimately repeat.

**Evidence:** `oil.csv` contains 43 missing price values among 1,218 rows; `transactions.csv` has 83,488 unique store-date rows across 1,682 dates; `holidays_events.csv` has 350 unique records but only 312 distinct dates, with 38 additional same-date records.

**Operational implication:** Naive inner joins or date-only holiday joins could drop sales rows or duplicate them.

**Potential action:** Use validated left joins, investigate transaction absence, apply time-aware oil imputation, and construct holiday features at the correct national/regional/local scope.

**Limitations:** Missing transaction rows may reflect store opening dates, closures, or source coverage; same-date holiday records are not automatically duplicates.

## Phase 2 — Cleaning and analytical scope

**Finding:** The complete sales panel is suitable for high-level analysis, while detailed work uses a deliberately selected and coverage-qualified subset.

**Evidence:** All joins preserved 3,000,888 rows and the unique date-store-family grain. Stores 44, 45, 17, 32, and 25 were selected after requiring at least 90% transaction and active-sales coverage. The subset contains Grocery I, Beverages, Produce, Cleaning, and Frozen Foods from 2015-08-16 through 2017-08-15.

**Operational implication:** A single high-volume store or product family would not represent the different planning challenges faced by large, typical, small, stable, and volatile operations.

**Potential action:** Retain the full population for network conclusions and use the subset for readable store-family comparisons and selected-series forecasting.

**Limitations:** The subset is intentionally representative, not statistically sampled. Seven later-opening or incompletely covered stores are retained in network totals but excluded from ordinary mature-store variability comparisons.

## Phase 3 — Exploratory demand evidence

### Demand is concentrated across stores and families

**Finding:** A relatively small set of stores and product families contributes a large share of observed sales.

**Evidence:** Store 44 has the highest total observed sales (approximately 62.09 million), followed by Stores 45, 47, 3, and 49. Grocery I accounts for 31.99% of family-level sales, followed by Beverages at 20.21%, Produce at 11.43%, and Cleaning at 9.08%.

**Operational implication:** Planning effort and supplier coordination should not be distributed uniformly across the portfolio.

**Potential action:** Give high-volume stores and families tighter exception monitoring while preserving differentiated policies for smaller categories.

**Limitations:** Sales values combine different product units and do not represent revenue, margin, or physical handling volume.

### Demand peaks are calendar-dependent

**Finding:** Average network demand is highest on weekends and in December.

**Evidence:** Sunday has the highest average daily sales (approximately 825,218), followed by Saturday (772,206). Month 12 has the highest average daily sales (808,565).

**Operational implication:** Labor, checkout, receiving, shelf-replenishment, and supplier requirements are unlikely to be uniform through the week or year.

**Potential action:** Review staffing, delivery windows, and replenishment frequency ahead of weekends and the year-end peak, then refine the pattern by store and family.

**Limitations:** Network averages can conceal different local or category-specific peak timing.

### Transactions are strongly associated with sales

**Finding:** Store traffic and observed sales move together at the store-day level.

**Evidence:** The Pearson correlation between store-day sales and transactions is 0.837 for available transaction records.

**Operational implication:** Traffic forecasting and checkout capacity are relevant to demand planning, but transaction volume does not fully explain product-mix or basket changes.

**Potential action:** Use transactions as a traffic indicator for staffing and capacity reviews, while keeping product-family demand as a separate planning measure.

**Limitations:** Correlation is descriptive, missing transaction records are not zeros, and the sales-per-transaction measure mixes product units.

### Promotion and holiday differences are associations

**Finding:** Promoted observations and holiday observations often show higher average sales, with substantial differences across categories.

**Evidence:** Holiday store-days average approximately 13,836 in sales versus 11,618 on non-holiday store-days, a descriptive difference of 19.09%. Among adequately represented promoted categories, observed promoted/non-promoted ratios vary widely; Produce is approximately 3.08.

**Operational implication:** Promotions and events may create category-specific demand and capacity pressure.

**Potential action:** Coordinate promotion calendars with staffing, receiving, shelf replenishment, and supplier planning; prioritize controlled tests for incremental lift.

**Limitations:** Promotion targeting, seasonality, store mix, and event timing confound these comparisons. They do not estimate causal lift.

### Demand regularity differs across store–family series

**Finding:** The portfolio contains substantial smooth, intermittent, lumpy, and erratic demand at store–family level.

**Evidence:** Among 1,782 store–family series, the ADI/CV² screen classifies 630 as Smooth, 593 as Intermittent, 324 as Lumpy, and 235 as Erratic. Fifty-three series have no positive historical sales.

**Operational implication:** One forecast-evaluation rule or review cadence is unlikely to fit every series.

**Potential action:** Evaluate forecast methods and review frequency by demand-pattern group, keeping all-zero and intermittent series visible as exceptions.

**Limitations:** These historical classifications do not specify safety stock, reorder points, or service targets.

### Semi-month dates are a descriptive planning signal

**Finding:** Network sales are higher around the 15th and month-end in the defined comparison window.

**Evidence:** Average daily network sales are 4.52% higher on the 15th, month-end, and their following days than on other dates. Personal Care, Cleaning, and Grocery I show positive family-level differences.

**Operational implication:** Semi-month dates may deserve explicit review in staffing, receiving, and replenishment calendars.

**Potential action:** Validate the pattern by store and year and test it after controlling for weekday, holidays, trend, and promotions.

**Limitations:** This is not a causal payday estimate.

### The April 2016 event window shows regional divergence

**Finding:** Sales changes in equal 30-day pre/post windows differ sharply by province.

**Evidence:** Average daily sales are 64.91% higher in Manabí and 24.92% higher in Guayas after 16 April 2016, while Santa Elena is 38.77% lower.

**Operational implication:** Exceptional events can create simultaneous surges, declines, and regional logistics differences.

**Potential action:** Maintain event-response scenarios and monitor local demand and store availability instead of applying one national adjustment.

**Limitations:** The pre/post comparison is temporally associated with the event and does not control for concurrent factors.

### Category changes co-move, but common shocks remain plausible

**Finding:** Several families have highly correlated daily log-sales changes.

**Evidence:** The matrix uses daily log-sales changes after removing the daily cross-family common component; the remaining positive and negative relationships show relative category co-movement.

**Operational implication:** Workload and replenishment pressure may peak across multiple categories at once.

**Potential action:** Review shared capacity constraints during common peak dates.

**Limitations:** Correlation does not establish complementarity, substitution, or causation and may reflect shared calendar or network shocks.

## Phase 4 — Operations analysis

### Demand level and variability require different controls

**Finding:** Product families divide into distinct demand/variability portfolios.

**Evidence:** The median-based segmentation contains 13 high-demand/stable, 4 high-demand/volatile, 3 low-demand/stable, and 13 low-demand/volatile families. High-demand/stable examples include Grocery I, Beverages, and Cleaning; high-demand/volatile examples include Produce, Home Care, and Frozen Foods.

**Operational implication:** High-volume stable flows are candidates for standardized routines, whereas high-volume volatile categories require flexibility and closer review.

**Potential action:** Use regular supplier and capacity cycles for stable families; use shorter review cycles, scenario ranges, and closer coordination for volatile important families.

**Limitations:** The median thresholds are transparent portfolio rules rather than universal industry benchmarks, and CV does not identify causes.

### Store lifecycle must be separated from store volatility

**Finding:** Store 25 is the most variable store among locations meeting the 90% transaction and active-sales coverage rule.

**Evidence:** Store 25 has a daily-demand CV of 0.702, 95.90% transaction coverage, and 96.08% active-sales coverage. Seven stores fail the coverage rule and are reported separately rather than ranked as ordinary mature operations.

**Operational implication:** Uniform network rules may understate local uncertainty, but late openings should not be mislabeled as demand volatility.

**Potential action:** Use store-specific planning tolerances for comparable mature stores and analyze opening/ramp-up locations with a separate lifecycle framework.

**Limitations:** Store mix, format, geography, and local events may explain some observed differences.

## Phase 5 — Forecasting support

### Forecast value differs by store-family series

**Finding:** The rolling one-day Random Forest has the lowest average MAE across the three selected validation series, but it is not the winner for every series.

**Evidence:** Average MAE is 414.41 for Random Forest, 647.09 for Holt-Winters, 718.64 for weekly seasonal naive, and 910.54 for one-day naive. Random Forest reduces average MAE by 42.33% versus seasonal naive in this validation design; Holt-Winters performs best for Store 32–Frozen Foods.

**Operational implication:** Forecasting can improve short-horizon visibility, but one universal model is not justified by this small comparison.

**Potential action:** Pilot forecasts beside a weekly seasonal-naive benchmark and monitor MAE/RMSLE by store-family before expanding complexity.

**Limitations:** The comparison covers three series and one 60-day historical holdout. It does not prove inventory savings, service improvement, or future stability.

## Phase 6 — Managerial synthesis

**Finding:** The evidence supports differentiated planning rather than one network-wide operating rule.

**Evidence:** Demand is concentrated, recurring weekend/year-end peaks are visible, high-demand families have different variability profiles, promotion associations are heterogeneous, and forecast winners vary by series.

**Operational implication:** Store, category, calendar, and uncertainty differences should shape staffing, capacity, replenishment review, promotional coordination, and forecasting cadence.

**Potential action:** Combine a stable core planning routine with exceptions for high-volume volatile families, high-variability mature stores, promotions, and recurring peak periods.

**Limitations:** Stock, stockout, order, lead-time, cost, margin, and service-level data are absent; precise inventory policies or financial impact claims are outside the evidence.
