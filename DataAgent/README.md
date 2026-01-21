# DataAgent - Comprehensive Data Analysis Platform

A full-featured data analysis application with multiple specialized agents for exploratory data analysis, forecasting, predictive modeling, recommendation systems, and interactive visualization.

## 🚀 Features

### Multiple Specialized Agents

1. **Cleaner Agent** (`agents/cleanerAgent.py`)
   - Data cleaning and preprocessing
   - BigQuery data fetching
   - AlloyDB connectivity
   - Missing value imputation
   - Duplicate removal

2. **Analyzer Agent** (`agents/analyzer.py`)
   - Comprehensive Exploratory Data Analysis (EDA)
   - Statistical analysis
   - Distribution analysis
   - Outlier detection
   - Correlation analysis
   - Automated HTML report generation

3. **Forecasting Agent** (`agents/forecastingAgent.py`)
   - **ARIMA** models for time series forecasting
   - **Prophet** (Facebook) for seasonal forecasting
   - **LSTM** neural networks for deep learning forecasting
   - Time series decomposition
   - Stationarity testing
   - Model comparison

4. **Prediction Agent** (`agents/predictionAgent.py`)
   - **Regression Models**: Linear, Ridge, Lasso, Random Forest, Gradient Boosting, SVM, Neural Networks
   - **Classification Models**: Logistic Regression, Random Forest, Gradient Boosting, SVM, Neural Networks
   - Automatic task type detection (classification vs regression)
   - Hyperparameter tuning with GridSearchCV
   - Cross-validation
   - Model comparison and selection

5. **Exploration Agent** (`agents/explorationAgent.py`)
   - Feature engineering
   - Feature selection (Mutual Information, F-test, PCA)
   - Anomaly detection
   - Insight generation
   - Actionable recommendations

6. **Test Agent** (`agents/testAgent.py`)
   - Comprehensive testing suite
   - Validates all agents and components
   - Tests MCP models
   - Generates test reports

### Model Context Protocol (MCP) Pattern

The project implements a Model Context Protocol pattern for managing models:

- **Model Factory** (`models/model_factory.py`): Creates and manages model instances
- **Model Context** (`models/model_context.py`): Holds model state, configuration, and metadata
- **Classification Registry** (`models/classification_models.py`): 11+ classification models
- **Recommendation Registry** (`models/recommendation_models.py`): Multiple recommendation algorithms

#### Available Classification Models:
- Logistic Regression
- Random Forest
- Gradient Boosting
- SVM
- Neural Network
- Naive Bayes
- K-Nearest Neighbors
- Decision Tree
- AdaBoost
- Extra Trees
- Voting Classifier

#### Available Recommendation Models:
- Collaborative Filtering
- Matrix Factorization (NMF/SVD)
- Content-Based Filtering
- Hybrid Recommendation System

### Interactive Dashboard

- **Modern Web Interface** built with Dash and Plotly
- **Multiple Tabs**:
  - Overview: Dataset statistics and metrics
  - Exploratory Analysis: Comprehensive EDA results
  - Visualizations: Interactive charts and graphs
  - Forecasting: Time series predictions
  - Predictions: ML model results
  - Insights: Automated recommendations
  - Data Table: Interactive data exploration

- **Features**:
  - Drag-and-drop CSV file upload
  - Real-time analysis
  - Interactive visualizations
  - Model performance metrics
  - Export capabilities

### View Architecture

HTML views are separated into the `views/` directory:
- `views/eda_report_view.py`: EDA HTML report generation
- `views/dashboard_views.py`: Dashboard tab components

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Step 1: Clone or Navigate to Project

```bash
cd DataAgent
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Settings

Edit `config.py` to set:
- BigQuery project and dataset (if using BigQuery)
- AlloyDB connection details (if using AlloyDB)
- Directory paths
- Model settings

### Step 5: Verify Installation

Run the test agent to verify everything is working:

```bash
python agents/testAgent.py
```

You should see all tests passing.

## 🎯 Usage

### Command Line Interface

#### Full Analysis Pipeline
```bash
python main.py --data datasets/your_data.csv --target target_column
```

#### Specific Analysis Modes
```bash
# EDA only
python main.py --mode eda --data datasets/your_data.csv

# Forecasting
python main.py --mode forecast --data datasets/your_data.csv --date-col date --value-col value

# Predictions
python main.py --mode predict --data datasets/your_data.csv --target target_column

# Exploration
python main.py --mode explore --data datasets/your_data.csv
```

#### BigQuery Integration
```bash
python main.py --bigquery --query "SELECT * FROM \`project.dataset.table\` LIMIT 10000"
```

#### Launch Dashboard
```bash
python main.py --dashboard --data datasets/your_data.csv
```

Or directly:
```bash
python dashboards/dashboard.py
```

Then open your browser to: `http://localhost:8050`

### Programmatic Usage

#### Basic Analysis
```python
from agents.cleanerAgent import Cleaner
from agents.analyzer import ModelAnalyzer
from agents.predictionAgent import PredictionAgent
import pandas as pd

# Load and clean data
cleaner = Cleaner()
df = pd.read_csv("your_data.csv")
df_cleaned = cleaner.clean_data(df)

# Run EDA
analyzer = ModelAnalyzer()
eda_results = analyzer.analyze_and_plot(df_cleaned, target_col="target")

# Train predictive models
predictor = PredictionAgent()
prediction_results = predictor.auto_train(df_cleaned, target_col="target")
```

#### Using MCP Pattern for Classification
```python
from models.model_factory import ModelFactory
import pandas as pd

factory = ModelFactory()

# Create and train a classification model
df = pd.read_csv("your_data.csv")
X = df.drop(columns=['target'])
y = df['target']

# Create model context
context = factory.create_classification_model('random_forest', {'n_estimators': 100})
context = factory.train_classification_model(context, X, y)

# Make predictions
predictions = context.predict(X.head(10))

# Save model
model_path = context.save()
print(f"Model saved to: {model_path}")

# Load model later
from models.model_context import ModelContext
loaded_context = ModelContext('random_forest', 'classification').load(model_path)
```

#### Using MCP Pattern for Recommendations
```python
from models.model_factory import ModelFactory
import pandas as pd

factory = ModelFactory()

# Create recommendation dataset (user_id, item_id, rating)
interactions = pd.DataFrame({
    'user_id': [1, 1, 2, 2, 3, 3],
    'item_id': [10, 20, 10, 30, 20, 30],
    'rating': [5, 4, 5, 3, 4, 5]
})

# Create and train recommendation model
context = factory.create_recommendation_model('collaborative_filtering')
context = factory.train_recommendation_model(context, interactions)

# Get recommendations for a user
recommendations = context.model.recommend_items(user_id=1, n_recommendations=5)
print(f"Recommendations: {recommendations}")
```

#### Time Series Forecasting
```python
from agents.forecastingAgent import ForecastingAgent
import pandas as pd

forecaster = ForecastingAgent()
df = pd.read_csv("time_series_data.csv")

# Prepare time series
ts = forecaster.prepare_time_series(df, date_col='date', value_col='value')

# Forecast using multiple models
results = forecaster.compare_forecasts(ts, forecast_periods=30)

# Access individual model forecasts
arima_forecast = results['arima']['forecast']
prophet_forecast = results['prophet']['forecast']
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python agents/testAgent.py
```

The test agent will:
- Test all agents (Cleaner, Analyzer, Forecasting, Prediction, Exploration)
- Test MCP classification models
- Test MCP recommendation models
- Test view components
- Generate a test report

## 📊 Output Structure

```
DataAgent/
├── reports/
│   ├── eda_report.html          # Comprehensive EDA report
│   ├── correlation_matrix.png   # Correlation heatmap
│   ├── distributions.png        # Distribution plots
│   ├── boxplots.png            # Outlier visualization
│   └── target_analysis.png     # Target variable analysis
│
├── models/
│   ├── arima_model.pkl         # ARIMA forecasting model
│   ├── prophet_model.pkl       # Prophet forecasting model
│   ├── lstm_model.h5          # LSTM model (if TensorFlow available)
│   ├── random_forest_*.pkl    # Prediction models
│   └── *_classification.pkl   # MCP classification models
│   └── *_recommendation.pkl   # MCP recommendation models
│
└── datasets/
    └── your_data.csv           # Input datasets
```

## 🔧 Configuration

Edit `config.py` to customize:

- **BigQuery Settings**: Project ID and dataset
- **AlloyDB Settings**: Connection parameters
- **Model Settings**: Random state, test size, validation size
- **Forecasting Settings**: Horizon, frequency
- **Directory Paths**: Reports, models, datasets

## 📈 Supported Models

### Forecasting
- ARIMA (Auto-ARIMA order selection)
- Prophet (with seasonality detection)
- LSTM (Long Short-Term Memory networks)

### Regression
- Linear Regression
- Ridge Regression
- Lasso Regression
- Random Forest Regressor
- Gradient Boosting Regressor
- Support Vector Regression (SVR)
- Multi-layer Perceptron (Neural Network)

### Classification (via MCP)
- Logistic Regression
- Random Forest
- Gradient Boosting
- Support Vector Machine (SVM)
- Multi-layer Perceptron (Neural Network)
- Naive Bayes
- K-Nearest Neighbors
- Decision Tree
- AdaBoost
- Extra Trees
- Voting Classifier

### Recommendation (via MCP)
- Collaborative Filtering
- Matrix Factorization (NMF/SVD)
- Content-Based Filtering
- Hybrid Recommendation System

## 🎨 Dashboard Features

The interactive dashboard provides:

1. **Data Upload**: Drag-and-drop CSV file upload
2. **Column Selection**: Automatic detection of date, numeric, and categorical columns
3. **Real-time Analysis**: Run full analysis pipeline with one click
4. **Interactive Visualizations**: 
   - Correlation matrices
   - Distribution plots
   - Box plots
   - Time series forecasts
   - Prediction vs Actual scatter plots
5. **Model Comparison**: Side-by-side comparison of multiple models
6. **Insights Panel**: Automated recommendations and data quality alerts

## 🔍 Example Workflow

1. **Load Data**: Upload CSV or connect to BigQuery
2. **Clean Data**: Automatic cleaning and preprocessing
3. **Explore**: Generate comprehensive EDA reports
4. **Engineer Features**: Create new features automatically
5. **Forecast**: Build time series models (if applicable)
6. **Predict**: Train multiple ML models and select best
7. **Recommend**: Build recommendation systems (if applicable)
8. **Visualize**: Interactive dashboard for exploration
9. **Export**: Save models and reports

## 🛠️ Dependencies

See `requirements.txt` for complete list. Key dependencies:

- pandas, numpy: Data manipulation
- scikit-learn: Machine learning
- statsmodels, prophet: Time series analysis
- plotly, dash: Interactive visualizations
- google-cloud-bigquery: BigQuery integration
- sqlalchemy, psycopg2: Database connectivity

## 📝 Notes

- **TensorFlow**: Optional dependency for LSTM forecasting. Install separately if needed:
  ```bash
  pip install tensorflow
  ```

- **BigQuery Authentication**: Ensure Google Cloud credentials are set up:
  ```bash
  export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
  ```

- **Large Datasets**: For very large datasets, consider sampling or using BigQuery for preprocessing

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run tests to verify installation
python agents/testAgent.py

# 3. Run analysis on sample data
python main.py --data datasets/bq-results-covid-open-data.csv

# 4. Launch dashboard
python main.py --dashboard
```

Then open your browser to `http://localhost:8050`

## 🏗️ Project Structure

```
DataAgent/
├── agents/              # All agent implementations
│   ├── cleanerAgent.py
│   ├── analyzer.py
│   ├── forecastingAgent.py
│   ├── predictionAgent.py
│   ├── explorationAgent.py
│   └── testAgent.py
├── models/              # MCP pattern implementation
│   ├── model_factory.py
│   ├── model_context.py
│   ├── classification_models.py
│   └── recommendation_models.py
├── views/               # HTML view templates
│   ├── eda_report_view.py
│   └── dashboard_views.py
├── dashboards/          # Dashboard application
│   └── dashboard.py
├── datasets/            # Input datasets
├── reports/             # Generated reports
├── models/              # Saved models
├── config.py            # Configuration
├── main.py              # Main entry point
└── requirements.txt     # Dependencies
```

## 🤝 Contributing

This is a comprehensive data analysis platform. Feel free to extend with:
- Additional forecasting models
- More visualization types
- Custom feature engineering functions
- Integration with other data sources
- Additional recommendation algorithms

## 📄 License

This project is provided as-is for data analysis purposes.

---

**Built with ❤️ for comprehensive data analysis**
