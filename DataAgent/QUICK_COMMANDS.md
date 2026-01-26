# Quick Command Reference

## 🚀 View Dashboard

```bash
cd /home/forhad/Study/personal/projects/DataAgent
python main.py --mode dashboard
```

**Access**: http://localhost:8050

---

## 📊 Run Specific Models

### Forecasting Models

```bash
# All forecasting models
python main.py --data datasets/your_data.csv --date-col date --value-col value --forecast-model all --mode forecast

# Only ARIMA
python main.py --data datasets/your_data.csv --date-col date --value-col value --forecast-model arima --mode forecast

# Only Prophet
python main.py --data datasets/your_data.csv --date-col date --value-col value --forecast-model prophet --mode forecast

# Only LSTM
python main.py --data datasets/your_data.csv --date-col date --value-col value --forecast-model lstm --mode forecast
```

### Prediction Models

```bash
# All prediction models
python main.py --data datasets/your_data.csv --target target_column --prediction-model all --mode predict

# Only Random Forest
python main.py --data datasets/your_data.csv --target target_column --prediction-model random_forest --mode predict

# Only Linear Regression
python main.py --data datasets/your_data.csv --target target_column --prediction-model linear_regression --mode predict

# Only Gradient Boosting
python main.py --data datasets/your_data.csv --target target_column --prediction-model gradient_boosting --mode predict

# Only Neural Network
python main.py --data datasets/your_data.csv --target target_column --prediction-model neural_network --mode predict
```

### Classification Models

```bash
# All classification models
python main.py --data datasets/your_data.csv --target target_column --classification-model all --mode predict

# Specific classification model
python main.py --data datasets/your_data.csv --target target_column --classification-model svm --mode predict

python main.py --data datasets/your_data.csv --target target_column --classification-model naive_bayes --mode predict
```

### Recommendation Models

```bash
# All recommendation models
python main.py --data datasets/your_data.csv --recommendation-model all --mode predict

# Specific recommendation model
python main.py --data datasets/your_data.csv --recommendation-model collaborative_filtering --mode predict
```

---

## 🎯 Combined: Specific Models + Dashboard

```bash
# ARIMA + Random Forest + Dashboard
python main.py \
    --data datasets/your_data.csv \
    --target target_column \
    --date-col date_column \
    --value-col value_column \
    --forecast-model arima \
    --prediction-model random_forest \
    --dashboard
```

---

## 📋 Full Analysis with Dashboard

```bash
python main.py \
    --data datasets/your_data.csv \
    --target target_column \
    --date-col date_column \
    --value-col value_column \
    --mode full \
    --dashboard
```

---

## 🔍 Available Model Options

### Forecasting: `--forecast-model`
- `all` (default)
- `arima`
- `prophet`
- `lstm`

### Prediction: `--prediction-model`
- `all` (default)
- `random_forest`
- `linear_regression`
- `ridge`
- `lasso`
- `gradient_boosting`
- `svr`
- `neural_network`

### Classification: `--classification-model`
- `all` (default)
- `logistic_regression`
- `random_forest`
- `gradient_boosting`
- `svm`
- `neural_network`
- `naive_bayes`
- `knn`
- `decision_tree`
- `adaboost`
- `extra_trees`
- `voting_classifier`

### Recommendation: `--recommendation-model`
- `all` (default)
- `collaborative_filtering`
- `matrix_factorization`
- `content_based`
- `hybrid`

---

**All HTML layout code is now in `views/dashboard_layout.py`**  
**All execution happens through `main.py`**
