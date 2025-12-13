import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os
from config import *

class DataScientist:

    def analyze_and_plot(self, df: pd.DataFrame):
        os.makedirs(REPORTS_DIR, exist_ok=True)
        numeric_cols = df.select_dtypes(include="number").columns
        corr = df[numeric_cols].corr()
        sns.heatmap(corr, annot=True)
        plt.savefig(f"{REPORTS_DIR}/correlation_matrix.png")
        plt.close()
        summary = df.describe().to_html()
        with open(f"{REPORTS_DIR}/eda_report.html", "w") as f:
            f.write(summary)
        return summary

    def train_model(self, df: pd.DataFrame, target_col: str):
        X = df.drop(columns=[target_col])
        y = df[target_col]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        print(classification_report(y_test, preds))
        os.makedirs(MODELS_DIR, exist_ok=True)
        joblib.dump(model, f"{MODELS_DIR}/model_{target_col}.pkl")
        return model
