# Data setup

This repository uses the Kaggle competition **Store Sales – Time Series Forecasting**. Raw files are not committed because they are large and remain subject to Kaggle's competition terms.

## Download

### Kaggle website

1. Open the [competition data page](https://www.kaggle.com/competitions/store-sales-time-series-forecasting/data).
2. Sign in, accept the competition rules if prompted, and download the archive.
3. Extract the CSV files into `data/raw/`.

### Kaggle CLI

After installing and configuring the [Kaggle API](https://github.com/Kaggle/kaggle-api):

```bash
kaggle competitions download -c store-sales-time-series-forecasting
unzip store-sales-time-series-forecasting.zip -d data/raw
```

## Expected placement

```text
data/raw/
├── train.csv
├── test.csv
├── stores.csv
├── transactions.csv
├── holidays_events.csv
├── oil.csv
└── sample_submission.csv
```

The code checks which files are actually present and reports missing inputs instead of assuming availability.

## File roles

| File | Role in the project |
|---|---|
| `train.csv` | Historical store-family daily sales and promotion counts; main demand fact table |
| `test.csv` | Future store-family dates and promotion counts for the competition horizon |
| `stores.csv` | Store location, type, and cluster attributes |
| `transactions.csv` | Observed daily transaction counts by store |
| `holidays_events.csv` | National, regional, and local holidays/events, including transferred-event flags |
| `oil.csv` | Daily WTI oil-price observations supplied by the competition |
| `sample_submission.csv` | Required Kaggle prediction format; used as a structure check |

## Data handling rules

- Preserve source files unchanged in `data/raw/`.
- Write cleaned data to `data/processed/` or `outputs/processed_data/`.
- Do not commit raw or generated large datasets.
- Record transformations and validate row counts, keys, and join coverage.
