import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import normaltest, shapiro
import warnings
warnings.filterwarnings('ignore')
import os
import hashlib
import pickle
from utils.common import setup_path
from config import *
setup_path()
from utils.segmentation import SegmentationAnalyzer

class ModelAnalyzer:
    """
    Comprehensive data analysis agent with extensive EDA capabilities
    """

    def __init__(self):
        self.reports_dir = REPORTS_DIR
        self.cache_dir = os.path.join(REPORTS_DIR, 'cache')
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        self.segmentation_analyzer = SegmentationAnalyzer()
        try:
            plt.style.use('seaborn-v0_8-darkgrid')
        except:
            try:
                plt.style.use('seaborn-darkgrid')
            except:
                plt.style.use('default')
        sns.set_palette("husl")
    
    def _get_cache_key(self, df: pd.DataFrame, target_col: str = None) -> str:
        """Generate cache key based on dataframe hash and target column"""
        # Create hash from dataframe shape, column names, and sample data
        df_hash = hashlib.md5(
            f"{df.shape}_{list(df.columns)}_{df.head(100).to_string()}".encode()
        ).hexdigest()
        cache_key = f"eda_{df_hash}_{target_col or 'none'}"
        return cache_key
    
    def _load_from_cache(self, cache_key: str) -> dict:
        """Load EDA results from cache if available"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except:
                return None
        return None
    
    def _save_to_cache(self, cache_key: str, results: dict):
        """Save EDA results to cache"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(results, f)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")

    def analyze_and_plot(self, df: pd.DataFrame, target_col: str = None, use_cache: bool = True) -> dict:
        """
        Comprehensive EDA with multiple visualizations and statistical analysis
        Uses caching to avoid re-processing the same dataset
        Limits to top columns to prevent memory issues
        """
        # Limit columns for EDA to prevent memory/image size issues
        MAX_EDA_COLS = 30
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) > MAX_EDA_COLS:
            print(f"⚠ Limiting EDA to top {MAX_EDA_COLS} numeric columns (out of {len(numeric_cols)}) to prevent memory issues")
            # Select top columns (prioritize those with less missing data)
            missing_pct = df[numeric_cols].isnull().sum() / len(df)
            top_cols = missing_pct.nsmallest(MAX_EDA_COLS).index.tolist()
            df_eda = df[top_cols + ([target_col] if target_col and target_col in df.columns else [])].copy()
        else:
            df_eda = df.copy()
        
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(df_eda, target_col)
            cached_results = self._load_from_cache(cache_key)
            if cached_results is not None:
                print("✓ Using cached EDA results (dataset already analyzed - skipping computation)")
                # Check if visualization files exist, regenerate if missing
                viz_files = ['correlation_matrix.png', 'distributions.png', 'boxplots.png']
                if target_col:
                    viz_files.append('target_analysis.png')
                
                missing_viz = [f for f in viz_files if not os.path.exists(os.path.join(self.reports_dir, f))]
                if missing_viz:
                    print(f"  Regenerating {len(missing_viz)} missing visualization(s)...")
                    self._generate_visualizations(df_eda, target_col)
                else:
                    print("  All visualizations already exist")
                
                return cached_results
        
        # Perform fresh analysis
        print("  Performing fresh EDA analysis...")
        results = {}
        
        # Basic statistics (on full dataset for completeness)
        results['basic_stats'] = self._basic_statistics(df)
        
        # Data quality report (on full dataset)
        results['data_quality'] = self._data_quality_report(df)
        
        # Correlation analysis (on limited dataset)
        results['correlation'] = self._correlation_analysis(df_eda)
        
        # Distribution analysis (on limited dataset)
        results['distributions'] = self._distribution_analysis(df_eda)
        
        # Outlier detection (on limited dataset)
        results['outliers'] = self._outlier_analysis(df_eda)
        
        # Segmentation analysis (on full dataset)
        results['segmentation'] = self.segmentation_analyzer.get_segmentation_summary(df)
        
        # Generate visualizations (on limited dataset)
        self._generate_visualizations(df_eda, target_col)
        
        # Generate HTML report
        results['html_report'] = self._generate_html_report(df, results)
        
        # Save to cache
        if use_cache:
            cache_key = self._get_cache_key(df_eda, target_col)
            self._save_to_cache(cache_key, results)
            print("✓ EDA results cached for future use")
        
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
        missing_values = df.isnull().sum()
        
        quality_report = {
            'missing_values': missing_values.to_dict(),
            'missing_percentage': (missing_values / len(df) * 100).to_dict(),
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
        corr_values = corr_matrix.values
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_values[i, j]
                if abs(corr_val) > 0.7:
                    high_corr_pairs.append({
                        'col1': corr_matrix.columns[i],
                        'col2': corr_matrix.columns[j],
                        'correlation': float(corr_val)
                    })
        
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'high_correlation_pairs': high_corr_pairs,
            'mean_absolute_correlation': float(corr_matrix.abs().mean().mean())
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
        """Generate comprehensive visualizations with safe limits to prevent memory issues"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Limit columns to prevent image size issues
        MAX_VIS_COLS = 20
        if len(numeric_cols) > MAX_VIS_COLS:
            numeric_cols = numeric_cols[:MAX_VIS_COLS]
        
        # 1. Correlation Heatmap (bounded size)
        if len(numeric_cols) > 1:
            plt.figure(figsize=(min(12, len(numeric_cols)), min(10, len(numeric_cols))))
            corr = df[numeric_cols].corr()
            # Only annotate if small enough
            annot = len(numeric_cols) <= 15
            sns.heatmap(corr, annot=annot, fmt='.2f', cmap='coolwarm', center=0,
                       square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
            plt.title('Correlation Matrix (Top Features)', fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.savefig(f"{self.reports_dir}/correlation_matrix.png", dpi=150, bbox_inches='tight')
            plt.close()
        
        # 2. Distribution plots - individual plots to avoid size issues
        if len(numeric_cols) > 0:
            # Limit to 9 columns max, create grid with capped height
            n_plot = min(9, len(numeric_cols))
            n_rows = (n_plot + 2) // 3
            max_height = min(5 * n_rows, 30)  # Cap at 30 inches
            fig, axes = plt.subplots(n_rows, 3, figsize=(15, max_height))
            
            # Flatten axes array properly
            if n_rows == 1:
                if isinstance(axes, np.ndarray):
                    axes = axes.flatten()
                else:
                    axes = [axes]
            else:
                axes = axes.flatten()
            
            for idx, col in enumerate(numeric_cols[:n_plot]):
                if idx < len(axes):
                    ax = axes[idx]
                    df[col].hist(bins=30, ax=ax, edgecolor='black', alpha=0.7)
                    ax.set_title(f'Distribution of {col}', fontweight='bold', fontsize=10)
                    ax.set_xlabel(col, fontsize=8)
                    ax.set_ylabel('Frequency', fontsize=8)
                    ax.grid(True, alpha=0.3)
            
            # Hide extra subplots
            for idx in range(n_plot, len(axes)):
                if idx < len(axes):
                    axes[idx].set_visible(False)
            
            plt.tight_layout()
            plt.savefig(f"{self.reports_dir}/distributions.png", dpi=150, bbox_inches='tight')
            plt.close()
        
        # 3. Box plots for outlier visualization (limited)
        if len(numeric_cols) > 0:
            n_cols_plot = min(6, len(numeric_cols))
            fig, axes = plt.subplots(1, n_cols_plot, figsize=(min(5*n_cols_plot, 30), 6))
            if n_cols_plot == 1:
                axes = [axes]
            
            for idx, col in enumerate(numeric_cols[:n_cols_plot]):
                if idx < len(axes):
                    ax = axes[idx]
                    df.boxplot(column=col, ax=ax, grid=True)
                    ax.set_title(f'Box Plot: {col}', fontweight='bold', fontsize=10)
                    ax.set_ylabel('Value', fontsize=8)
            
            plt.tight_layout()
            plt.savefig(f"{self.reports_dir}/boxplots.png", dpi=150, bbox_inches='tight')
            plt.close()
        
        # 4. Pair plot (only for very small datasets)
        if len(numeric_cols) <= 6 and len(df) < 5000:
            try:
                sns.pairplot(df[numeric_cols], diag_kind='kde')
                plt.savefig(f"{self.reports_dir}/pairplot.png", dpi=150, bbox_inches='tight')
                plt.close()
            except:
                pass  # Skip if fails
        
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
                # Sample for Q-Q plot if too large
                sample_data = df[target_col].dropna()
                if len(sample_data) > 10000:
                    sample_data = sample_data.sample(10000, random_state=42)
                stats.probplot(sample_data, dist="norm", plot=plt)
                plt.title(f'Q-Q Plot: {target_col}', fontweight='bold')
                plt.tight_layout()
                plt.savefig(f"{self.reports_dir}/target_analysis.png", dpi=150, bbox_inches='tight')
                plt.close()
            else:
                # Classification target
                plt.figure(figsize=(10, 6))
                value_counts = df[target_col].value_counts().head(20)  # Limit to top 20
                value_counts.plot(kind='bar', edgecolor='black', alpha=0.7)
                plt.title(f'Distribution of {target_col}', fontweight='bold')
                plt.xlabel(target_col)
                plt.ylabel('Count')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(f"{self.reports_dir}/target_analysis.png", dpi=150, bbox_inches='tight')
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
