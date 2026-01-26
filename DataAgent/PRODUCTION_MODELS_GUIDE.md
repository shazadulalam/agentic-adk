# Production-Grade Machine Learning Models Guide

## Overview

The DataAgent platform now includes a comprehensive production-grade model training and management system that works with **any CSV or Excel data**. All models are automatically saved with proper naming conventions and can be loaded for inference.

## Model Types

### 1. Forecasting Models

#### ARIMA Model (`arima_model.pkl`)
- **Purpose**: Time series forecasting using AutoRegressive Integrated Moving Average
- **Use Case**: Univariate time series data with trend and seasonality
- **Requirements**: Date column and value column
- **Usage**:
  ```python
  from agents.forecastingAgent import ForecastingAgent
  forecaster = ForecastingAgent()
  ts = forecaster.prepare_time_series(df, 'date_col', 'value_col')
  result = forecaster.forecast_arima(ts, forecast_periods=30)
  ```

#### Prophet Model (`prophet_model.pkl`)
- **Purpose**: Facebook Prophet for time series with strong seasonality
- **Use Case**: Time series with multiple seasonality patterns (daily, weekly, yearly)
- **Requirements**: Date column and value column
- **Usage**:
  ```python
  result = forecaster.forecast_prophet(df, 'date_col', 'value_col', forecast_periods=30)
  ```

#### LSTM Model (`lstm_model.h5`)
- **Purpose**: Deep learning LSTM for complex time series patterns
- **Use Case**: Non-linear time series with long-term dependencies
- **Requirements**: TensorFlow, date column and value column
- **Usage**:
  ```python
  result = forecaster.forecast_lstm(ts, forecast_periods=30)
  ```

### 2. Prediction Models

#### Random Forest Models (`random_forest_*.pkl`)
- **Regression**: `random_forest_regression.pkl`
- **Classification**: `random_forest_classification.pkl`
- **Purpose**: Ensemble tree-based models for both regression and classification
- **Use Case**: Works well with any tabular data
- **Usage**: Automatically trained when target column is specified

#### Other Prediction Models
- `linear_regression_regression.pkl`
- `ridge_regression.pkl`
- `lasso_regression.pkl`
- `gradient_boosting_regression.pkl`
- `svr_regression.pkl`
- `neural_network_regression.pkl`

### 3. MCP Classification Models (`*_classification.pkl`)

All classification models follow the naming convention: `{model_name}_classification.pkl`

Available models:
- `logistic_regression_classification.pkl`
- `random_forest_classification.pkl`
- `gradient_boosting_classification.pkl`
- `svm_classification.pkl`
- `neural_network_classification.pkl`
- `naive_bayes_classification.pkl`
- `knn_classification.pkl`
- `decision_tree_classification.pkl`
- `adaboost_classification.pkl`
- `extra_trees_classification.pkl`
- `voting_classifier_classification.pkl`

### 4. MCP Recommendation Models (`*_recommendation.pkl`)

All recommendation models follow the naming convention: `{model_name}_recommendation.pkl`

Available models:
- `collaborative_filtering_recommendation.pkl`
- `matrix_factorization_recommendation.pkl`
- `content_based_recommendation.pkl`
- `hybrid_recommendation.pkl`

## Universal Data Loading

The platform includes a universal data loader that works with any CSV or Excel file:

```python
from utils.data_loader import UniversalDataLoader

loader = UniversalDataLoader()

# Load CSV or Excel
df = loader.load('path/to/data.csv')
df = loader.load('path/to/data.xlsx', sheet_name=0)

# Validate data
validation = loader.validate_data(df)
print(f"Rows: {validation['rows']}, Columns: {validation['columns']}")
```

### Supported Formats
- CSV (`.csv`) - with automatic encoding detection
- Excel (`.xlsx`, `.xls`, `.xlsm`, `.xlsb`)

## Production Training Pipeline

### Using the Production Trainer

```python
from models.production_trainer import ProductionModelTrainer

trainer = ProductionModelTrainer()

# Train all models
results = trainer.train_all_models(
    data_path='path/to/data.csv',  # or DataFrame
    target_col='target_column',     # for prediction/classification
    date_col='date_column',          # for forecasting
    value_col='value_column',        # for forecasting
    forecast_periods=30
)

# List all trained models
saved_models = trainer.list_trained_models()
```

### Command Line Usage

```bash
# Train all models on a CSV file
python main.py --data datasets/your_data.csv \
               --target target_column \
               --date-col date_column \
               --value-col value_column \
               --mode full

# Train only prediction models
python main.py --data datasets/your_data.csv \
               --target target_column \
               --mode predict

# Train only forecasting models
python main.py --data datasets/your_data.csv \
               --date-col date_column \
               --value-col value_column \
               --mode forecast
```

## Model Manager

The `ModelManager` class handles all model saving and loading:

```python
from models.model_manager import ModelManager

manager = ModelManager()

# Save a model
model_path = manager.save_forecasting_model(model, 'arima')
model_path = manager.save_prediction_model(model, 'random_forest', 'regression')
model_path = manager.save_classification_model(model, 'logistic_regression')
model_path = manager.save_recommendation_model(model, 'collaborative_filtering')

# Load a model
model = manager.load_model(model_path)

# List all saved models
all_models = manager.list_saved_models()
```

## Model Metadata

All models are saved with metadata including:
- Model path
- Model type/name
- Training timestamp
- Performance metrics (accuracy, R², RMSE, etc.)
- Training parameters

Metadata is stored in `models/model_metadata.json`

## File Structure

```
models/
├── arima_model.pkl              # ARIMA forecasting model
├── prophet_model.pkl            # Prophet forecasting model
├── lstm_model.h5                # LSTM model (if TensorFlow available)
├── lstm_scaler.pkl              # LSTM scaler
├── random_forest_regression.pkl # Random Forest regression
├── random_forest_classification.pkl # Random Forest classification
├── linear_regression_regression.pkl
├── ridge_regression.pkl
├── lasso_regression.pkl
├── *_classification.pkl         # MCP classification models
├── *_recommendation.pkl         # MCP recommendation models
└── model_metadata.json          # Model metadata
```

## Best Practices

1. **Data Preparation**: Ensure your data is clean before training
   ```python
   from agents.cleanerAgent import Cleaner
   cleaner = Cleaner()
   df_clean = cleaner.clean_data(df)
   ```

2. **Feature Engineering**: Use the exploration agent for feature engineering
   ```python
   from agents.explorationAgent import ExplorationAgent
   explorer = ExplorationAgent()
   df_engineered = explorer.feature_engineering(df)
   ```

3. **Memory Management**: The system automatically handles large datasets by:
   - Sampling to max 50,000 rows for training
   - Limiting features to top 300 by variance
   - Using float32 for memory efficiency

4. **Model Selection**: The system automatically selects the best model based on:
   - Classification: Accuracy
   - Regression: R² Score

## Loading Saved Models for Inference

```python
from models.model_manager import ModelManager

manager = ModelManager()

# Load a specific model
arima_model = manager.load_forecasting_model('arima')
rf_model = manager.load_model('models/random_forest_regression.pkl')

# Make predictions
predictions = rf_model.predict(X_new)
```

## Troubleshooting

### Model Not Found
- Check if model exists: `manager.model_exists('arima')`
- List all models: `manager.list_saved_models()`

### Memory Issues
- The system automatically samples data and limits features
- For very large datasets, consider preprocessing before training

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Prophet is optional: `pip install prophet` (if needed)
- TensorFlow is optional: `pip install tensorflow` (for LSTM)

## Example: Complete Workflow

```python
from utils.data_loader import UniversalDataLoader
from models.production_trainer import ProductionModelTrainer
from agents.cleanerAgent import Cleaner

# 1. Load data
loader = UniversalDataLoader()
df = loader.load('your_data.csv')

# 2. Clean data
cleaner = Cleaner()
df_clean = cleaner.clean_data(df)

# 3. Train all models
trainer = ProductionModelTrainer()
results = trainer.train_all_models(
    df_clean,
    target_col='target',
    date_col='date',
    value_col='value'
)

# 4. Check saved models
saved = trainer.list_trained_models()
print(f"Trained {len(saved)} models")

# 5. Load and use a model
model = trainer.load_model('models/random_forest_regression.pkl')
predictions = model.predict(X_new)
```

---

**Note**: All models are production-ready and work with any CSV or Excel data format. The system automatically handles data preprocessing, feature engineering, and model selection.
