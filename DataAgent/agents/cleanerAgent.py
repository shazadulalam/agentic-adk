import pandas as pd
from google.cloud import bigquery
from sqlalchemy import create_engine

class Cleaner:

    def fetch_bigquery_data(self, query:str) -> pd.DataFrame:
        client = bigquery.Client(project=BIGQUERY_PROJECT)
        df = client.query(query).to_dataframe()
        return df

    def fetch_alloydb_data(self, table_name: str) -> pd.DataFrame:
        conn_str = f"postgresql+psycopg2://{ALLOYDB_USER}:{ALLOYDB_PASSWORD}@{ALLOYDB_HOST}:{ALLOYDB_PORT}/{ALLOYDB_DB}"
        engine = create_engine(conn_str)
        df = pd.read_sql_table(table_name, engine)
        return df

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.drop_duplicates()
        df = df.fillna(df.median(numeric_only=True))
        return df