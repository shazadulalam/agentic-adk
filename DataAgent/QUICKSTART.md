# Quick Start Guide

## Installation

```bash
# Install all dependencies
pip install -r requirements.txt
```

## Basic Usage

### 1. Run Full Analysis Pipeline

```bash
python main.py --data datasets/bq-results-covid-open-data.csv
```

This will:
- Load and clean the data
- Run comprehensive EDA
- Generate visualizations
- Train predictive models
- Save reports to `reports/` directory
- Save models to `models/` directory

### 2. Launch Interactive Dashboard

```bash
python main.py --dashboard
# OR
python dashboards/dashboard.py
```

Then open your browser to: `http://localhost:8050`

### 3. Run Specific Analysis

```bash
# EDA only
python main.py --mode eda --data your_data.csv

# Forecasting (requires date and value columns)
python main.py --mode forecast --data your_data.csv --date-col date --value-col value

# Predictions (requires target column)
python main.py --mode predict --data your_data.csv --target target_column
```

### 4. Use BigQuery

```bash
python main.py --bigquery --query "SELECT * FROM \`project.dataset.table\` LIMIT 10000"
```

## Dashboard Features

1. **Upload Data**: Drag and drop CSV files
2. **Configure**: Select target, date, and value columns
3. **Run Analysis**: Click "Run Full Analysis" button
4. **Explore**: Navigate through different tabs:
   - Overview: Dataset statistics
   - Exploratory Analysis: EDA results
   - Visualizations: Interactive charts
   - Forecasting: Time series predictions
   - Predictions: ML model results
   - Insights: Automated recommendations
   - Data Table: Browse your data

## Example Workflow

```python
from agents.cleanerAgent import Cleaner
from agents.analyzer import ModelAnalyzer
from agents.predictionAgent import PredictionAgent
import pandas as pd

# Load data
df = pd.read_csv("your_data.csv")

# Clean
cleaner = Cleaner()
df_clean = cleaner.clean_data(df)

# Analyze
analyzer = ModelAnalyzer()
results = analyzer.analyze_and_plot(df_clean, target_col="target")

# Predict
predictor = PredictionAgent()
models = predictor.auto_train(df_clean, target_col="target")
print(f"Best model: {models['best_model']}")
```

## Output Files

- **Reports**: `reports/eda_report.html`, `reports/correlation_matrix.png`, etc.
- **Models**: `models/*.pkl` (saved models for later use)

## Troubleshooting

1. **Import Errors**: Make sure all dependencies are installed
2. **BigQuery Errors**: Set up Google Cloud credentials
3. **Memory Issues**: Use smaller datasets or sample your data
4. **Dashboard Not Loading**: Check if port 8050 is available

## Next Steps

- Customize `config.py` for your environment
- Add your own datasets to `datasets/` directory
- Explore the generated reports in `reports/` directory
- Use saved models for predictions on new data
