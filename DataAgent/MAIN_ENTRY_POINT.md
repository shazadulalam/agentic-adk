# Main Entry Point - main.py

## Overview

**`main.py` is now the single entry point** for the entire DataAgent platform. All functionality including dashboard, visualizations, forecasting, and models are accessible through `main.py`.

## Architecture

- **`main.py`**: Single entry point with all functionality
- **`dashboards/dashboard.py`**: Now a module (not executed directly)
- All visualization, forecasting, and model training integrated in `main.py`

## Usage Commands

### 1. Launch Dashboard Only

```bash
cd /home/forhad/Study/personal/projects/DataAgent
python main.py --mode dashboard
```

Or use the convenience script:
```bash
bash run_dashboard.sh
```

**Access**: http://localhost:8050

### 2. Run Full Analysis + Dashboard

```bash
python main.py --data datasets/your_data.csv --target target_column --dashboard
```

This will:
1. Load and clean data
2. Run EDA analysis
3. Generate insights
4. Train forecasting models (if date/value columns provided)
5. Train prediction models
6. Launch dashboard with results

### 3. Run Analysis Only (No Dashboard)

```bash
python main.py --data datasets/your_data.csv --target target_column --mode full
```

### 4. Run Specific Analysis Modes

```bash
# EDA only
python main.py --data datasets/your_data.csv --mode eda

# Forecasting only
python main.py --data datasets/your_data.csv --date-col date_column --value-col value_column --mode forecast

# Predictions only
python main.py --data datasets/your_data.csv --target target_column --mode predict

# Exploration only
python main.py --data datasets/your_data.csv --mode explore
```

## Command Line Arguments

```
--data PATH              Path to data file (CSV/Excel) [default: datasets/bq-results-covid-open-data.csv]
--bigquery               Fetch data from BigQuery instead of local file
--query SQL              BigQuery SQL query
--target COLUMN          Target column for predictions
--date-col COLUMN        Date column for forecasting
--value-col COLUMN       Value column for forecasting
--mode MODE              Analysis mode: full, eda, forecast, predict, explore, dashboard
--dashboard              Launch interactive dashboard after analysis
```

## What's Integrated in main.py

### ✅ Dashboard
- File upload (CSV/Excel)
- Date range filtering
- Real-time metrics
- Interactive visualizations
- All tabs (Overview, EDA, Visualizations, Forecasting, Predictions, Insights, Data Table)

### ✅ Data Analysis
- Data loading (CSV/Excel/BigQuery)
- Data cleaning
- Exploratory Data Analysis (EDA)
- Feature engineering
- Insights generation

### ✅ Forecasting Models
- ARIMA model
- Prophet model
- LSTM model
- All saved as: `arima_model.pkl`, `prophet_model.pkl`, `lstm_model.h5`

### ✅ Prediction Models
- Random Forest (regression & classification)
- Linear/Ridge/Lasso Regression
- Gradient Boosting
- SVM
- Neural Networks
- All saved with proper naming: `random_forest_*.pkl`, etc.

### ✅ MCP Models
- Classification models: `*_classification.pkl`
- Recommendation models: `*_recommendation.pkl`

## Workflow Examples

### Example 1: Quick Dashboard
```bash
python main.py --mode dashboard
```
Opens dashboard immediately with default dataset (if available)

### Example 2: Full Analysis Pipeline
```bash
python main.py \
    --data datasets/your_data.csv \
    --target sales \
    --date-col date \
    --value-col revenue \
    --mode full \
    --dashboard
```
Runs complete analysis and launches dashboard with results

### Example 3: Analysis Then Manual Dashboard
```bash
# Step 1: Run analysis
python main.py --data datasets/your_data.csv --target sales --mode full

# Step 2: Launch dashboard separately
python main.py --mode dashboard
```

## File Structure

```
DataAgent/
├── main.py                    # ⭐ SINGLE ENTRY POINT - Everything here
├── dashboards/
│   └── dashboard.py          # Module (not executed directly)
├── agents/                   # Analysis agents
├── models/                   # ML models
├── views/                    # HTML templates
└── utils/                    # Utilities
```

## Benefits

1. **Single Entry Point**: Everything accessible through `main.py`
2. **Unified Workflow**: Analysis and dashboard in one command
3. **Flexible**: Can run analysis only, dashboard only, or both
4. **Consistent**: Same data flow for all operations
5. **Maintainable**: All logic in one place

## Migration Notes

- **Old way**: `python dashboards/dashboard.py` ❌
- **New way**: `python main.py --mode dashboard` ✅

- **Old way**: Run analysis separately, then dashboard separately
- **New way**: `python main.py --data file.csv --target col --dashboard` ✅

## Quick Reference

| Task | Command |
|------|---------|
| Dashboard only | `python main.py --mode dashboard` |
| Full analysis | `python main.py --data file.csv --target col --mode full` |
| Analysis + Dashboard | `python main.py --data file.csv --target col --dashboard` |
| EDA only | `python main.py --data file.csv --mode eda` |
| Forecasting only | `python main.py --data file.csv --date-col date --value-col value --mode forecast` |
| Predictions only | `python main.py --data file.csv --target col --mode predict` |

---

**All functionality is now in `main.py` - the single entry point for the entire platform!**
