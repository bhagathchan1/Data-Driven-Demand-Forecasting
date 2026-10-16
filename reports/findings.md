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

## Recommended scope for Phase 2

**Finding:** The complete sales panel is suitable for high-level analysis, but detailed store-family analysis should use a deliberately selected subset rather than an arbitrary sample.

**Evidence:** The full training data contains 3,000,888 rows across 54 stores, 33 product families, and 1,684 dates. Store and family importance, variability, and contextual-data completeness have not yet been evaluated on the cleaned merged panel.

**Operational implication:** A single high-volume store or product family would not represent the different planning challenges faced by large, typical, small, stable, and volatile operations.

**Potential action:** Retain the full population for overall trends. For detailed analysis, select up to five stores representing two high-volume stores, one near-median-volume store, one low-volume store, and one high-variability store; select four leading families plus one operationally important volatile family; use the latest 24 months to balance recency and seasonality. Final IDs should be chosen only after Notebook 02 validates joins and completeness.

**Limitations:** This is a selection framework, not a final sample. Scope choices may change if missing transactions, store opening dates, prolonged zero-sales periods, or other quality findings make a candidate unsuitable.
