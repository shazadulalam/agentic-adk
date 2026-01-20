import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_regression, f_classif, mutual_info_regression, mutual_info_classif
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class ExplorationAgent:
    """
    Agent for data exploration, feature engineering, and insights generation
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
    
    def feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply common feature engineering techniques"""
        df_engineered = df.copy()
        
        # Extract datetime features if datetime columns exist
        for col in df_engineered.columns:
            if df_engineered[col].dtype == 'datetime64[ns]':
                df_engineered[f'{col}_year'] = df_engineered[col].dt.year
                df_engineered[f'{col}_month'] = df_engineered[col].dt.month
                df_engineered[f'{col}_day'] = df_engineered[col].dt.day
                df_engineered[f'{col}_dayofweek'] = df_engineered[col].dt.dayofweek
                df_engineered[f'{col}_is_weekend'] = df_engineered[col].dt.dayofweek >= 5
        
        # Create interaction features for numeric columns
        numeric_cols = df_engineered.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) >= 2:
            # Create ratio features for top correlated pairs
            corr_matrix = df_engineered[numeric_cols].corr().abs()
            top_pairs = []
            
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    if corr_matrix.iloc[i, j] > 0.5:
                        top_pairs.append((
                            corr_matrix.columns[i],
                            corr_matrix.columns[j],
                            corr_matrix.iloc[i, j]
                        ))
            
            # Create ratio features for top 3 pairs
            for col1, col2, _ in sorted(top_pairs, key=lambda x: x[2], reverse=True)[:3]:
                # Avoid division by zero
                df_engineered[f'{col1}_div_{col2}'] = df_engineered[col1] / (df_engineered[col2] + 1e-8)
                df_engineered[f'{col1}_mul_{col2}'] = df_engineered[col1] * df_engineered[col2]
        
        # Polynomial features for highly skewed columns
        for col in numeric_cols:
            if abs(df_engineered[col].skew()) > 2:
                df_engineered[f'{col}_squared'] = df_engineered[col] ** 2
                df_engineered[f'{col}_sqrt'] = np.sqrt(df_engineered[col].abs())
        
        return df_engineered
    
    def feature_selection(self, X: pd.DataFrame, y: pd.Series, 
                         method: str = 'mutual_info', k: int = 10) -> dict:
        """
        Select best features using various methods
        Methods: 'mutual_info', 'f_test', 'pca'
        """
        results = {}
        
        # Determine if classification or regression
        is_classification = len(y.unique()) / len(y) < 0.1 or y.dtype == 'object'
        
        if method == 'mutual_info':
            if is_classification:
                selector = SelectKBest(score_func=mutual_info_classif, k=k)
            else:
                selector = SelectKBest(score_func=mutual_info_regression, k=k)
            
            selector.fit(X, y)
            selected_features = X.columns[selector.get_support()].tolist()
            feature_scores = dict(zip(X.columns, selector.scores_))
            
            results = {
                'selected_features': selected_features,
                'feature_scores': feature_scores,
                'method': 'mutual_information'
            }
        
        elif method == 'f_test':
            if is_classification:
                selector = SelectKBest(score_func=f_classif, k=k)
            else:
                selector = SelectKBest(score_func=f_regression, k=k)
            
            selector.fit(X, y)
            selected_features = X.columns[selector.get_support()].tolist()
            feature_scores = dict(zip(X.columns, selector.scores_))
            
            results = {
                'selected_features': selected_features,
                'feature_scores': feature_scores,
                'method': 'f_test'
            }
        
        elif method == 'pca':
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Apply PCA
            pca = PCA(n_components=min(k, X.shape[1]))
            X_pca = pca.fit_transform(X_scaled)
            
            # Get feature importance from PCA
            feature_importance = np.abs(pca.components_).sum(axis=0)
            feature_scores = dict(zip(X.columns, feature_importance))
            selected_features = sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)[:k]
            selected_features = [feat[0] for feat in selected_features]
            
            results = {
                'selected_features': selected_features,
                'feature_scores': feature_scores,
                'explained_variance_ratio': pca.explained_variance_ratio_.tolist(),
                'cumulative_variance': np.cumsum(pca.explained_variance_ratio_).tolist(),
                'method': 'pca'
            }
        
        return results
    
    def generate_insights(self, df: pd.DataFrame, target_col: str = None) -> dict:
        """Generate actionable insights from the data"""
        insights = {
            'data_quality': [],
            'patterns': [],
            'recommendations': []
        }
        
        # Data quality insights
        missing_pct = (df.isnull().sum() / len(df) * 100)
        high_missing = missing_pct[missing_pct > 30]
        if len(high_missing) > 0:
            insights['data_quality'].append(
                f"Warning: {len(high_missing)} columns have >30% missing values. "
                f"Consider imputation or removal: {', '.join(high_missing.index.tolist())}"
            )
        
        if df.duplicated().sum() > 0:
            insights['data_quality'].append(
                f"Found {df.duplicated().sum()} duplicate rows. Consider removing duplicates."
            )
        
        # Pattern insights
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr().abs()
            high_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if corr_val > 0.8:
                        high_corr.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_val))
            
            if high_corr:
                insights['patterns'].append(
                    f"Found {len(high_corr)} highly correlated feature pairs (>0.8). "
                    "Consider removing one to reduce multicollinearity."
                )
        
        # Outlier insights
        for col in numeric_cols[:5]:  # Check first 5 numeric columns
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
            if outliers > len(df) * 0.05:  # More than 5% outliers
                insights['patterns'].append(
                    f"Column '{col}' has {outliers} outliers ({outliers/len(df)*100:.1f}%). "
                    "Consider outlier treatment."
                )
        
        # Recommendations
        if target_col and target_col in df.columns:
            if df[target_col].dtype in [np.number]:
                # Regression task
                if df[target_col].skew() > 2:
                    insights['recommendations'].append(
                        f"Target variable '{target_col}' is highly skewed. "
                        "Consider log transformation."
                    )
            else:
                # Classification task
                class_dist = df[target_col].value_counts()
                if len(class_dist) > 2 and (class_dist.min() / class_dist.max()) < 0.1:
                    insights['recommendations'].append(
                        f"Target variable '{target_col}' has imbalanced classes. "
                        "Consider using class weights or resampling techniques."
                    )
        
        # Feature engineering recommendations
        if len(numeric_cols) < 10:
            insights['recommendations'].append(
                "Dataset has relatively few features. Consider feature engineering "
                "to create interaction terms or polynomial features."
            )
        
        return insights
    
    def detect_anomalies(self, df: pd.DataFrame, method: str = 'isolation_forest') -> dict:
        """Detect anomalies in the dataset"""
        from sklearn.ensemble import IsolationForest
        from sklearn.cluster import DBSCAN
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return {'error': 'No numeric columns for anomaly detection'}
        
        X = df[numeric_cols].fillna(df[numeric_cols].median())
        
        if method == 'isolation_forest':
            model = IsolationForest(contamination=0.1, random_state=42)
            anomalies = model.fit_predict(X)
            anomaly_indices = df.index[anomalies == -1].tolist()
        
        elif method == 'dbscan':
            model = DBSCAN(eps=0.5, min_samples=5)
            clusters = model.fit_predict(X)
            anomaly_indices = df.index[clusters == -1].tolist()
        
        else:
            return {'error': f'Unknown method: {method}'}
        
        return {
            'anomaly_count': len(anomaly_indices),
            'anomaly_percentage': len(anomaly_indices) / len(df) * 100,
            'anomaly_indices': anomaly_indices,
            'method': method
        }
    
    def create_summary_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create comprehensive summary statistics"""
        summary = pd.DataFrame({
            'Column': df.columns,
            'Data Type': df.dtypes.values,
            'Non-Null Count': df.count().values,
            'Null Count': df.isnull().sum().values,
            'Null Percentage': (df.isnull().sum() / len(df) * 100).values,
            'Unique Count': [df[col].nunique() for col in df.columns]
        })
        
        # Add numeric-specific statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            idx = summary[summary['Column'] == col].index[0]
            summary.loc[idx, 'Mean'] = df[col].mean()
            summary.loc[idx, 'Median'] = df[col].median()
            summary.loc[idx, 'Std'] = df[col].std()
            summary.loc[idx, 'Min'] = df[col].min()
            summary.loc[idx, 'Max'] = df[col].max()
            summary.loc[idx, 'Skewness'] = df[col].skew()
        
        return summary
