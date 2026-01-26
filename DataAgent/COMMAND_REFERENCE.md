# Command Line Reference Guide

## Quick Commands

### View Dashboard Only

```bash
cd /home/forhad/Study/personal/projects/DataAgent
python main.py --mode dashboard
```

**Access**: http://localhost:8050

### Run Full Analysis + Dashboard

```bash
python main.py --data datasets/your_data.csv --target target_column --dashboard
```

### Run Specific Models

#### Forecasting Models

```bash
# Train all forecasting models
python main.py --data datasets/your_data.csv --date-col date_column --value-col value_column --forecast-model all --mode forecast

# Train only ARIMA
python main.py --data datasets/your_data.csv --date-col date_column --value-col value_column --forecast-model arima --mode forecast

# Train only Prophet
python main.py --data datasets/your_data.csv --date-col date_column --value-col value_column --forecast-model prophet --mode forecast

# Train only LSTM
python main.py --data datasets/your_data.csv --date-col date_column --value-col value_column --forecast-model lstm --mode forecast
```

#### Prediction Models (Regression/Classification)

```bash
# Train all prediction models
python main.py --data datasets/your_data.csv --target target_column --prediction-model all --mode predict

# Train only Random Forest
python main.py --data datasets/your_data.csv --target target_column --prediction-model random_forest --mode predict

# Train only Linear Regression
python main.py --data datasets/your_data.csv --target target_column --prediction-model linear_regression --mode predict

# Train only Gradient Boosting
python main.py --data datasets/your_data.csv --target target_column --prediction-model gradient_boosting --mode predict

# Train only Neural Network
python main.py --data datasets/your_data.csv --target target_column --prediction-model neural_network --mode predict
```

#### MCP Classification Models

```bash
# Train all classification models
python main.py --data datasets/your_data.csv --target target_column --classification-model all --mode predict

# Train specific classification model
python main.py --data datasets/your_data.csv --target target_column --classification-model logistic_regression --mode predict

python main.py --data datasets/your_data.csv --target target_column --classification-model random_forest --mode predict

python main.py --data datasets/your_data.csv --target target_column --classification-model svm --mode predict

python main.py --data datasets/your_data.csv --target target_column --classification-model naive_bayes --mode predict
```

#### MCP Recommendation Models

```bash
# Train all recommendation models
python main.py --data datasets/your_data.csv --recommendation-model all --mode predict

# Train specific recommendation model
python main.py --data datasets/your_data.csv --recommendation-model collaborative_filtering --mode predict

python main.py --data datasets/your_data.csv --recommendation-model matrix_factorization --mode predict
```

### Combined: Run Specific Models + Dashboard

```bash
# Run ARIMA forecasting + Random Forest prediction + Dashboard
python main.py \
    --data datasets/your_data.csv \
    --target target_column \
    --date-col date_column \
    --value-col value_column \
    --forecast-model arima \
    --prediction-model random_forest \
    --dashboard
```

## Available Models

### Forecasting Models
- `arima` - ARIMA time series forecasting
- `prophet` - Facebook Prophet forecasting
- `lstm` - LSTM neural network forecasting
- `all` - Train all forecasting models

### Prediction Models (Regression)
- `linear_regression` - Linear Regression
- `ridge` - Ridge Regression
- `lasso` - Lasso Regression
- `random_forest` - Random Forest Regressor
- `gradient_boosting` - Gradient Boosting Regressor
- `svr` - Support Vector Regression
- `neural_network` - Neural Network Regressor
- `all` - Train all regression models

### Prediction Models (Classification)
- `logistic_regression` - Logistic Regression
- `random_forest` - Random Forest Classifier
- `gradient_boosting` - Gradient Boosting Classifier
- `svm` - Support Vector Machine
- `neural_network` - Neural Network Classifier
- `all` - Train all classification models

### MCP Classification Models
- `logistic_regression` - Logistic Regression
- `random_forest` - Random Forest
- `gradient_boosting` - Gradient Boosting
- `svm` - Support Vector Machine
- `neural_network` - Neural Network
- `naive_bayes` - Naive Bayes
- `knn` - K-Nearest Neighbors
- `decision_tree` - Decision Tree
- `adaboost` - AdaBoost
- `extra_trees` - Extra Trees
- `voting_classifier` - Voting Classifier
- `all` - Train all classification models

### MCP Recommendation Models
- `collaborative_filtering` - Collaborative Filtering
- `matrix_factorization` - Matrix Factorization
- `content_based` - Content-Based Filtering
- `hybrid` - Hybrid Recommendation
- `all` - Train all recommendation models

## Examples

### Example 1: Dashboard Only
```bash
python main.py --mode dashboard
```
Opens dashboard at http://localhost:8050

### Example 2: Full Analysis with All Models
```bash
python main.py \
    --data datasets/your_data.csv \
    --target sales \
    --date-col date \
    --value-col revenue \
    --mode full \
    --dashboard
```

### Example 3: Train Only ARIMA and Random Forest
```bash
python main.py \
    --data datasets/your_data.csv \
    --target sales \
    --date-col date \
    --value-col revenue \
    --forecast-model arima \
    --prediction-model random_forest \
    --mode full
```

### Example 4: Train Specific Classification Model
```bash
python main.py \
    --data datasets/your_data.csv \
    --target category \
    --classification-model svm \
    --mode predict
```

### Example 5: Train Recommendation Model
```bash
python main.py \
    --data datasets/user_item_data.csv \
    --recommendation-model collaborative_filtering \
    --mode predict
```

## Command Structure

```bash
python main.py \
    --data PATH \                    # Data file path
    --target COLUMN \                # Target column
    --date-col COLUMN \              # Date column (for forecasting)
    --value-col COLUMN \             # Value column (for forecasting)
    --mode MODE \                    # full, eda, forecast, predict, explore, dashboard
    --forecast-model MODEL \         # all, arima, prophet, lstm
    --prediction-model MODEL \       # all, random_forest, linear_regression, etc.
    --classification-model MODEL \   # all, logistic_regression, svm, etc.
    --recommendation-model MODEL \   # all, collaborative_filtering, etc.
    --dashboard                      # Launch dashboard after analysis
```

---

**All commands run through `main.py` - the single entry point!**
