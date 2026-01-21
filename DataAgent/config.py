import os

# BigQuery
BIGQUERY_PROJECT = "agenticdataproject"
BIGQUERY_DATASET = "bigquery-public-data.covid19_open_data"

# AlloyDB
ALLOYDB_HOST = "localhost"
ALLOYDB_PORT = "5432"
ALLOYDB_DB = "mydb"
ALLOYDB_USER = "user"
ALLOYDB_PASSWORD = "password"

# Directories
REPORTS_DIR = "reports"
MODELS_DIR = "models"
DATASETS_DIR = "datasets"
CACHE_DIR = os.path.join(REPORTS_DIR, "cache")

# Model Settings
RANDOM_STATE = 42
TEST_SIZE = 0.2
VALIDATION_SIZE = 0.1

# Forecasting Settings
FORECAST_HORIZON = 30  # days
FORECAST_FREQ = 'D'  # daily frequency
