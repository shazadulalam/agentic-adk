import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import normaltest, shapiro
import warnings
warnings.filterwarnings('ignore')
import os
from config import *

class ModelAnalyzer:
    """
    Comprehensive data analysis agent with extensive EDA capabilities
    """

    def __init__(self):
        self.reports_dir = REPORTS_DIR
        os.makedirs(self.reports_dir, exist_ok=True)
        try:
            plt.style.use('seaborn-v0_8-darkgrid')
        except:
            try:
                plt.style.use('seaborn-darkgrid')
            except:
                plt.style.use('default')
        sns.set_palette("husl")

    def analyze_and_plot(self, df: pd.DataFrame, target_col: str = None) -> dict:
        """
        Comprehensive EDA with multiple visualizations and statistical analysis
        """
        results = {}
        
        # Basic statistics
        results['basic_stats'] = self._basic_statistics(df)
        
        # Data quality report
        results['data_quality'] = self._data_quality_report(df)
        
        # Correlation analysis
        results['correlation'] = self._correlation_analysis(df)
        
        # Distribution analysis
        results['distributions'] = self._distribution_analysis(df)
        
        # Outlier detection
        results['outliers'] = self._outlier_analysis(df)
        
        # Generate visualizations
        self._generate_visualizations(df, target_col)
        
        # Generate HTML report
        results['html_report'] = self._generate_html_report(df, results)
        
        return results

    def _basic_statistics(self, df: pd.DataFrame) -> dict:
        """Calculate basic statistical measures"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        stats_dict = {
            'shape': df.shape,
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'numeric_summary': df[numeric_cols].describe().to_dict(),
            'categorical_summary': {}
        }
        
        # Categorical summary
        for col in df.select_dtypes(include=['object', 'category']).columns:
            stats_dict['categorical_summary'][col] = {
                'unique_count': df[col].nunique(),
                'top_values': df[col].value_counts().head(10).to_dict(),
                'null_count': df[col].isnull().sum()
            }
        
        return stats_dict

    def _data_quality_report(self, df: pd.DataFrame) -> dict:
        """Generate data quality report"""
        quality_report = {
            'missing_values': df.isnull().sum().to_dict(),
            'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'data_types': df.dtypes.to_dict(),
            'columns_with_high_missing': []
        }
        
        # Identify columns with high missing percentage
        for col, pct in quality_report['missing_percentage'].items():
            if pct > 50:
                quality_report['columns_with_high_missing'].append({
                    'column': col,
                    'missing_percentage': pct
                })
        
        return quality_report

    def _correlation_analysis(self, df: pd.DataFrame) -> dict:
        """Perform correlation analysis"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {'error': 'Insufficient numeric columns for correlation analysis'}
        
        corr_matrix = df[numeric_cols].corr()
        
        # Find highly correlated pairs
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    high_corr_pairs.append({
                        'col1': corr_matrix.columns[i],
                        'col2': corr_matrix.columns[j],
                        'correlation': corr_val
                    })
        
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'high_correlation_pairs': high_corr_pairs,
            'mean_absolute_correlation': corr_matrix.abs().mean().mean()
        }

    def _distribution_analysis(self, df: pd.DataFrame) -> dict:
        """Analyze distributions of numeric columns"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        distributions = {}
        
        for col in numeric_cols:
            data = df[col].dropna()
            
            # Normality tests
            try:
                stat, p_value = normaltest(data)
                is_normal = p_value > 0.05
            except:
                is_normal = None
                p_value = None
            
            distributions[col] = {
                'skewness': stats.skew(data),
                'kurtosis': stats.kurtosis(data),
                'is_normal': is_normal,
                'normality_p_value': p_value,
                'mean': data.mean(),
                'median': data.median(),
                'std': data.std(),
                'min': data.min(),
                'max': data.max(),
                'q25': data.quantile(0.25),
                'q75': data.quantile(0.75),
                'iqr': data.quantile(0.75) - data.quantile(0.25)
            }
        
        return distributions

    def _outlier_analysis(self, df: pd.DataFrame, method: str = 'iqr') -> dict:
        """Detect outliers using IQR or Z-score method"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outliers = {}
        
        for col in numeric_cols:
            data = df[col].dropna()
            
            if method == 'iqr':
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outlier_mask = (data < lower_bound) | (data > upper_bound)
            else:  # z-score
                z_scores = np.abs(stats.zscore(data))
                outlier_mask = z_scores > 3
            
            outliers[col] = {
                'count': outlier_mask.sum(),
                'percentage': (outlier_mask.sum() / len(data)) * 100,
                'indices': data[outlier_mask].index.tolist() if outlier_mask.any() else []
            }
        
        return outliers

    def _generate_visualizations(self, df: pd.DataFrame, target_col: str = None):
        """Generate comprehensive visualizations"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # 1. Correlation Heatmap
        if len(numeric_cols) > 1:
            plt.figure(figsize=(12, 10))
            corr = df[numeric_cols].corr()
            sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                       square=True, linewidths=1, cbar_kws={"shrink": 0.8})
            plt.title('Correlation Matrix', fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.savefig(f"{self.reports_dir}/correlation_matrix.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        # 2. Distribution plots for numeric columns
        n_cols = len(numeric_cols)
        if n_cols > 0:
            n_rows = (n_cols + 2) // 3
            fig, axes = plt.subplots(n_rows, 3, figsize=(15, 5*n_rows))
            axes = axes.flatten() if n_cols > 1 else [axes]
            
            for idx, col in enumerate(numeric_cols[:9]):  # Limit to 9 plots
                ax = axes[idx]
                df[col].hist(bins=30, ax=ax, edgecolor='black', alpha=0.7)
                ax.set_title(f'Distribution of {col}', fontweight='bold')
                ax.set_xlabel(col)
                ax.set_ylabel('Frequency')
                ax.grid(True, alpha=0.3)
            
            # Hide extra subplots
            for idx in range(len(numeric_cols), len(axes)):
                axes[idx].set_visible(False)
            
            plt.tight_layout()
            plt.savefig(f"{self.reports_dir}/distributions.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        # 3. Box plots for outlier visualization
        if len(numeric_cols) > 0:
            n_cols_plot = min(6, len(numeric_cols))
            fig, axes = plt.subplots(1, n_cols_plot, figsize=(5*n_cols_plot, 6))
            if n_cols_plot == 1:
                axes = [axes]
            
            for idx, col in enumerate(numeric_cols[:n_cols_plot]):
                ax = axes[idx]
                df.boxplot(column=col, ax=ax, grid=True)
                ax.set_title(f'Box Plot: {col}', fontweight='bold')
                ax.set_ylabel('Value')
            
            plt.tight_layout()
            plt.savefig(f"{self.reports_dir}/boxplots.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        # 4. Pair plot (if reasonable number of columns)
        if len(numeric_cols) <= 6 and len(df) < 10000:
            sns.pairplot(df[numeric_cols], diag_kind='kde')
            plt.savefig(f"{self.reports_dir}/pairplot.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        # 5. Target variable analysis (if provided)
        if target_col and target_col in df.columns:
            if df[target_col].dtype in [np.number]:
                # Regression target
                plt.figure(figsize=(12, 5))
                plt.subplot(1, 2, 1)
                df[target_col].hist(bins=30, edgecolor='black', alpha=0.7)
                plt.title(f'Distribution of {target_col}', fontweight='bold')
                plt.xlabel(target_col)
                plt.ylabel('Frequency')
                
                plt.subplot(1, 2, 2)
                stats.probplot(df[target_col].dropna(), dist="norm", plot=plt)
                plt.title(f'Q-Q Plot: {target_col}', fontweight='bold')
                plt.tight_layout()
                plt.savefig(f"{self.reports_dir}/target_analysis.png", dpi=300, bbox_inches='tight')
                plt.close()
            else:
                # Classification target
                plt.figure(figsize=(10, 6))
                df[target_col].value_counts().plot(kind='bar', edgecolor='black', alpha=0.7)
                plt.title(f'Distribution of {target_col}', fontweight='bold')
                plt.xlabel(target_col)
                plt.ylabel('Count')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(f"{self.reports_dir}/target_analysis.png", dpi=300, bbox_inches='tight')
                plt.close()

    def _generate_html_report(self, df: pd.DataFrame, results: dict) -> str:
        """Generate comprehensive HTML report using view"""
        from views.eda_report_view import EDAReportView
        return EDAReportView.generate_html_report(df, results)

    def train_model(self, df: pd.DataFrame, target_col: str):
        """Legacy method for backward compatibility"""
        from agents.predictionAgent import PredictionAgent
        predictor = PredictionAgent()
        return predictor.auto_train(df, target_col)
