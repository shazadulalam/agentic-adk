from agents.cleanerAgent import Cleaner
from agents.analyzer import ModelAnalyzer
import pandas as pd

def main():
    de = Cleaner()
    ds = ModelAnalyzer()

    # Fetch Data
    try:
        query = f"SELECT * FROM `{de.__class__.__name__}` LIMIT 1000"
        df = de.fetch_bigquery_data(query)
    except:
        df = pd.read_csv("datasets/bq-results-covid-open-data.csv")

    df = de.clean_data(df)

    # EDA and Report
    ds.analyze_and_plot(df)

    # Train Model
    target_col = "target" if "target" in df.columns else df.columns[-1]
    ds.train_model(df, target_col)

if __name__ == "__main__":
    main()
