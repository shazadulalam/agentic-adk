import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


class FeatureEngineeringStrategies:
    
    def __init__(self):
        self.feature_info = {
            'per_capita': {'name': 'Per-Capita Normalization', 'description': 'Normalize features by population or other denominator to enable fair comparisons across regions', 'use_cases': ['Epidemiological data', 'Regional comparisons', 'Population-based metrics'], 'formula': 'feature_per_capita = feature_value / population'},
            'rolling_means': {'name': 'Rolling Means / Lags', 'description': 'Create moving averages and lagged features to capture temporal patterns and trends', 'use_cases': ['Time series smoothing', 'Trend detection', 'Noise reduction'], 'formula': 'rolling_mean = mean(values[t-window:t])'},
            'growth_rate': {'name': 'Growth Rate Features', 'description': 'Calculate percentage change, growth rates, and acceleration metrics', 'use_cases': ['Growth analysis', 'Rate of change', 'Acceleration detection'], 'formula': 'growth_rate = (value[t] - value[t-1]) / value[t-1] * 100'},
            'log_transform': {'name': 'Log Transformations', 'description': 'Apply logarithmic transformations to handle skewed distributions and multiplicative relationships', 'use_cases': ['Skewed data', 'Multiplicative relationships', 'Variance stabilization'], 'formula': 'log_feature = log(feature + 1)'},
            'interaction': {'name': 'Interaction Features', 'description': 'Create multiplicative or additive interactions between features (e.g., cases × population)', 'use_cases': ['Feature relationships', 'Non-linear patterns', 'Domain knowledge'], 'formula': 'interaction = feature1 × feature2'},
            'temporal': {'name': 'Temporal Encodings', 'description': 'Extract time-based features like day-of-week, month, wave index, and cyclical patterns', 'use_cases': ['Seasonality', 'Cyclical patterns', 'Time-based grouping'], 'formula': 'day_of_week = datetime.dayofweek, wave_index = calculate_wave_number()'}
        }
    
    def per_capita_normalization(self, df, value_col, population_col=None, default_population=100000):
        population = df[population_col] if population_col and population_col in df.columns else default_population
        population = population.replace(0, default_population)
        return (df[value_col] / population) * 100000
    
    def rolling_means_and_lags(self, df, value_col, date_col=None, window_sizes=[7, 14, 30], lags=[1, 7, 14]):
        df_result = df.copy()
        if date_col and date_col in df.columns:
            df_result = df_result.sort_values(date_col).reset_index(drop=True)
        for window in window_sizes:
            df_result[f'{value_col}_rolling_mean_{window}'] = df_result[value_col].rolling(window=window, min_periods=1).mean()
        for lag in lags:
            df_result[f'{value_col}_lag_{lag}'] = df_result[value_col].shift(lag)
        return df_result
    
    def growth_rate_features(self, df, value_col, date_col=None):
        df_result = df.copy()
        if date_col and date_col in df.columns:
            df_result = df_result.sort_values(date_col).reset_index(drop=True)
        df_result[f'{value_col}_pct_change'] = df_result[value_col].pct_change() * 100
        df_result[f'{value_col}_abs_change'] = df_result[value_col].diff()
        df_result[f'{value_col}_growth_rate_7d'] = ((df_result[value_col] - df_result[value_col].shift(7)) / df_result[value_col].shift(7) * 100)
        df_result[f'{value_col}_acceleration'] = df_result[f'{value_col}_pct_change'].diff()
        return df_result.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    def log_transformations(self, df, value_cols, add_one=True):
        df_result = df.copy()
        value_cols = [value_cols] if isinstance(value_cols, str) else value_cols
        for col in value_cols:
            if col in df.columns:
                df_result[f'{col}_log'] = np.log1p(df_result[col]) if add_one else np.log(df_result[col].replace(0, np.nan))
        return df_result
    
    def interaction_features(self, df, feature1, feature2, operations=['multiply', 'divide', 'add', 'subtract']):
        df_result = df.copy()
        if feature1 not in df.columns or feature2 not in df.columns:
            return df_result
        ops = {'multiply': lambda x, y: x * y, 'divide': lambda x, y: x / y.replace(0, np.nan), 'add': lambda x, y: x + y, 'subtract': lambda x, y: x - y}
        for op in operations:
            if op in ops:
                df_result[f'{feature1}_{op[0]}_{feature2}'] = ops[op](df_result[feature1], df_result[feature2])
        return df_result
    
    def temporal_encodings(self, df, date_col):
        df_result = df.copy()
        if date_col not in df.columns:
            return df_result
        df_result[date_col] = pd.to_datetime(df_result[date_col], errors='coerce')
        df_result['year'] = df_result[date_col].dt.year
        df_result['month'] = df_result[date_col].dt.month
        df_result['day'] = df_result[date_col].dt.day
        df_result['day_of_week'] = df_result[date_col].dt.dayofweek
        df_result['day_of_year'] = df_result[date_col].dt.dayofyear
        df_result['week'] = df_result[date_col].dt.isocalendar().week
        df_result['quarter'] = df_result[date_col].dt.quarter
        df_result['month_sin'] = np.sin(2 * np.pi * df_result['month'] / 12)
        df_result['month_cos'] = np.cos(2 * np.pi * df_result['month'] / 12)
        df_result['day_of_week_sin'] = np.sin(2 * np.pi * df_result['day_of_week'] / 7)
        df_result['day_of_week_cos'] = np.cos(2 * np.pi * df_result['day_of_week'] / 7)
        return self._calculate_wave_index(df_result, date_col)
    
    def _calculate_wave_index(self, df, date_col, threshold_col=None, threshold_percentile=50):
        df_result = df.copy()
        if threshold_col is None:
            numeric_cols = df_result.select_dtypes(include=[np.number]).columns
            threshold_col = numeric_cols[0] if len(numeric_cols) > 0 else None
        if threshold_col is None:
            df_result['wave_index'] = 0
            return df_result
        df_result = df_result.sort_values(date_col).reset_index(drop=True)
        threshold = df_result[threshold_col].quantile(threshold_percentile / 100)
        above_threshold = (df_result[threshold_col] > threshold).astype(int)
        wave_changes = above_threshold.diff().fillna(0)
        df_result['wave_index'] = (wave_changes > 0).cumsum()
        return df_result
    
    def apply_all_strategies(self, df, value_col, date_col=None, population_col=None, interaction_cols=None, apply_log=True):
        df_result = df.copy()
        df_result[f'{value_col}_per_capita'] = self.per_capita_normalization(df_result, value_col, population_col)
        df_result = self.rolling_means_and_lags(df_result, value_col, date_col)
        df_result = self.growth_rate_features(df_result, value_col, date_col)
        if apply_log:
            df_result = self.log_transformations(df_result, value_col)
        if interaction_cols:
            for col in interaction_cols:
                if col in df_result.columns:
                    df_result = self.interaction_features(df_result, value_col, col, operations=['multiply', 'divide'])
        if date_col and date_col in df_result.columns:
            df_result = self.temporal_encodings(df_result, date_col)
        return df_result
    
    def get_strategy_info(self):
        return self.feature_info
    
    def get_strategy_summary(self):
        return [{'key': k, 'name': v['name'], 'description': v['description'], 'use_cases': ', '.join(v['use_cases']), 'formula': v['formula']} for k, v in self.feature_info.items()]


if __name__ == "__main__":
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    sample_df = pd.DataFrame({'date': dates, 'cases': np.random.randint(100, 1000, 100), 'population': np.random.randint(100000, 1000000, 100)})
    fe = FeatureEngineeringStrategies()
    result_df = fe.apply_all_strategies(sample_df, value_col='cases', date_col='date', population_col='population', interaction_cols=['population'])
    print(f"Original columns: {len(sample_df.columns)}")
    print(f"After feature engineering: {len(result_df.columns)}")
    print(f"\nNew features created:")
    for col in sorted(set(result_df.columns) - set(sample_df.columns)):
        print(f"  - {col}")
