# Data-Driven Demand Analysis and Forecasting for Grocery Retail Operations

An MBA Year-1 Operations Management project supported by data science, using the Kaggle **Store Sales – Time Series Forecasting** competition data.

## Project background

Grocery retailers must plan labor, replenishment, store capacity, promotions, and supplier coordination despite demand that varies by date, location, category, and external events. This project examines those demand patterns and develops forecasting support without reducing the business problem to a model leaderboard exercise.

## Business problem

**How can historical sales and operational factors be analyzed to understand demand patterns and support better retail planning decisions?**

The project explores how historical sales, promotions, store characteristics, holidays, transactions, and other contextual variables can support better retail demand and operational planning.

Because the dataset does not include stock-on-hand, replenishment orders, lead times, service levels, or stockouts, the project will discuss possible inventory implications but will not claim to optimize inventory directly.

## Objectives

1. Understand historical retail demand patterns.
2. Identify factors associated with changes in sales.
3. Examine differences across stores and product families.
4. Explore the operational impact of promotions, holidays, and demand variability.
5. Develop a suitable forecasting approach for selected demand series.
6. Translate analytical findings into practical operational insights.

## Dataset

- Source: [Kaggle — Store Sales: Time Series Forecasting](https://www.kaggle.com/competitions/store-sales-time-series-forecasting)
- Local location: `data/raw/` (ignored by Git)
- Observed competition files: `train.csv`, `test.csv`, `stores.csv`, `transactions.csv`, `holidays_events.csv`, `oil.csv`, and `sample_submission.csv`

See [`data/README.md`](data/README.md) for download and placement instructions. Raw competition files are intentionally excluded from version control.

## Methodology

The project follows a business-first sequence:

1. Data understanding and quality profiling
2. Cleaning, careful integration, and validation
3. Focused exploratory analysis of demand patterns
4. Operations analysis of variability, store performance, promotions, and peaks
5. Baseline-led forecasting with chronological validation
6. Evidence-based managerial implications and limitations

Forecast accuracy will be considered in terms of decision usefulness. Causal claims will not be made from descriptive promotion, holiday, transaction, or oil-price associations alone.

## Repository structure

```text
.
├── README.md
├── DATA_SCIENCE_CANVAS.md   # Strategic project canvas (problem, data, models, ops)
├── Presentation.md          # 18-slide MBA presentation brief
├── requirements.txt
├── data/
│   ├── raw/                 # Local Kaggle CSVs; ignored by Git
│   ├── processed/           # Curated analysis data
│   └── README.md
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_exploratory_data_analysis.ipynb
│   ├── 04_operations_analysis.ipynb
│   ├── 05_forecasting.ipynb
│   └── 06_managerial_insights.ipynb
├── src/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── eda.py               # Advanced demand classification & shock analytics
│   ├── features.py
│   ├── visualization.py
│   └── forecasting.py
├── reports/
│   ├── figures/
│   ├── tables/
│   ├── findings.md
│   └── final_report_outline.md
└── outputs/
    ├── processed_data/
    ├── forecasts/
    └── model_results/
```

## Installation

Python 3.9 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python3 -m pip install -r requirements.txt
```

## Running the notebooks

1. Download and extract the Kaggle CSVs as described in `data/README.md`.
2. Start Jupyter from the repository root:

   ```bash
   jupyter lab
   ```

3. Run notebooks in numerical order. Each notebook uses relative paths and is designed to run from the repository root or the `notebooks/` directory.

For a non-interactive reproducibility check:

```bash
python3 -m nbconvert --execute --to notebook --inplace notebooks/01_data_understanding.ipynb
```

## How the analysis builds the MBA story

Each notebook answers a different business question and separates evidence from interpretation:

| Notebook | Main question | Business use |
|---|---|---|
| 01 — Data understanding | What do the source files represent, and are their grains and keys reliable? | Establishes what can and cannot be claimed from the data |
| 02 — Cleaning | How should the sources be prepared without losing genuine retail signals? | Produces a validated panel and a justified analytical scope |
| 03 — EDA | Where do demand patterns differ over time, by store, family, promotion, and event context? | Identifies patterns worth operational attention |
| 04 — Operations analysis | Which demand patterns create planning issues? | Connects variability and peaks to staffing, capacity, replenishment, and coordination |
| 05 — Forecasting | Do transparent forecasts improve on practical baselines? | Tests whether forecasting adds decision support rather than becoming the project objective |
| 06 — Managerial insights | What should a manager learn or consider doing? | Converts evidence into qualified actions and limitations |

Important figures are saved at presentation resolution in `reports/figures/`, and compact supporting tables are saved in `reports/tables/`. Interpretations follow the structure **Finding → Evidence → Operational implication → Possible action → Limitation**, making them reusable in the written report and presentation.

The completed business-oriented analysis is available in [`reports/final_report.md`](reports/final_report.md). It includes a clear explanation of why a confusion matrix is not appropriate for continuous sales forecasting and documents the correct regression metrics and validation evidence.

A detailed record of every analytical step, validation check, output, and business interpretation is available in [`PROJECT_SUMMARY.md`](PROJECT_SUMMARY.md). This is the recommended starting point for explaining the workflow during an MBA viva or project review.

A copy-ready, slide-by-slide brief for generating the MBA presentation is available in [`Presentation.md`](Presentation.md). It contains validated figures, chart references, speaker notes, limitations, and instructions for a presentation-generating LLM.

Every numbered notebook step begins with **Why this step is needed** before the code. Non-obvious transformations also include focused comments explaining grain protection, join validation, lifecycle coverage, leakage prevention, and model comparison logic, making the notebooks suitable for a new reader or project viva.

## Key analytical questions

- How does demand change over time, across weekdays, months, and seasons?
- Which stores and product families contribute the most demand, and which are most variable?
- How do transactions and sales patterns differ across store types, clusters, and locations?
- How are promotions and holidays associated with demand, and how heterogeneous are those relationships?
- When do peaks create implications for staffing, capacity, replenishment, and supplier coordination?
- Do simple, transparent forecasts provide enough improvement over operational baselines to support planning?

## Project status

**Analytical pipeline complete:** all six notebooks have been executed successfully using the seven verified Kaggle source files. The repository now includes a validated analytical subset, 19 presentation-ready analytical figures, a project canvas, compact evidence tables, forecast validation results, and an evidence-linked managerial action register. Raw Kaggle data remains local and excluded from Git.

## Academic disclaimer

This is an academic MBA project using publicly available competition data. It is not an operational deployment, professional consulting advice, or a claim of causal impact. Findings are limited by the variables and historical context available in the dataset.
