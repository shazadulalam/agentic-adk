import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class SegmentationAnalyzer:
    def __init__(self):
        self.demographic_keywords = {
            'age', 'birth', 'year', 'old', 'generation', 'gender', 'sex', 'male', 'female',
            'income', 'salary', 'wage', 'earnings', 'revenue_personal', 'education', 'degree',
            'school', 'university', 'college', 'marital', 'married', 'single', 'divorced',
            'relationship', 'status', 'household', 'family_size', 'children', 'kids'
        }
        self.geographic_keywords = {
            'country', 'nation', 'city', 'town', 'state', 'province', 'region', 'area',
            'address', 'street', 'zip', 'postal', 'code', 'location', 'latitude', 'longitude',
            'continent', 'timezone', 'currency', 'language', 'locale'
        }
        self.firmographic_keywords = {
            'company', 'firm', 'business', 'organization', 'corp', 'inc', 'llc',
            'size', 'employees', 'headcount', 'revenue', 'sales', 'turnover', 'industry',
            'sector', 'vertical', 'domain', 'performance', 'profit', 'margin', 'growth',
            'market_cap', 'valuation', 'founded', 'established'
        }
        self.behavioral_keywords = {
            'purchase', 'buy', 'transaction', 'order', 'cart', 'checkout', 'spend', 'expenditure',
            'engagement', 'active', 'inactive', 'visit', 'session', 'click', 'view', 'browse',
            'status', 'user_status', 'customer_status', 'loyalty', 'frequency', 'recency',
            'churn', 'retention', 'conversion', 'action', 'behavior', 'pattern', 'habit'
        }
        self.technographic_keywords = {
            'device', 'phone', 'mobile', 'tablet', 'desktop', 'laptop', 'os', 'operating_system',
            'platform', 'browser', 'software', 'app', 'application', 'tool', 'technology',
            'adoption', 'usage', 'version', 'update', 'upgrade', 'integration', 'api'
        }
        self.psychographic_keywords = {
            'lifestyle', 'interest', 'hobby', 'preference', 'value', 'belief', 'opinion',
            'attitude', 'personality', 'trait', 'motivation', 'goal', 'aspiration', 'concern',
            'priority', 'satisfaction', 'happiness', 'wellbeing', 'health', 'fitness'
        }
    
    def detect_segmentation_type(self, column_name: str, sample_values: pd.Series) -> str:
        col_lower = column_name.lower()
        
        if any(kw in col_lower for kw in self.demographic_keywords):
            return 'demographic'
        if any(kw in col_lower for kw in self.geographic_keywords):
            return 'geographic'
        if any(kw in col_lower for kw in self.firmographic_keywords):
            return 'firmographic'
        if any(kw in col_lower for kw in self.behavioral_keywords):
            return 'behavioral'
        if any(kw in col_lower for kw in self.technographic_keywords):
            return 'technographic'
        if any(kw in col_lower for kw in self.psychographic_keywords):
            return 'psychographic'
        
        return 'other'
    
    def analyze_segmentation(self, df: pd.DataFrame) -> Dict:
        segmentation = {
            'demographic': [],
            'geographic': [],
            'firmographic': [],
            'behavioral': [],
            'technographic': [],
            'psychographic': [],
            'other': []
        }
        
        for col in df.columns:
            seg_type = self.detect_segmentation_type(col, df[col])
            segmentation[seg_type].append({
                'column': col,
                'type': df[col].dtype.name,
                'unique_count': df[col].nunique(),
                'null_count': df[col].isnull().sum(),
                'sample_values': df[col].dropna().head(5).tolist() if df[col].dtype == 'object' else None
            })
        
        return segmentation
    
    def get_segmentation_summary(self, df: pd.DataFrame) -> Dict:
        seg_analysis = self.analyze_segmentation(df)
        summary = {}
        
        for seg_type, columns in seg_analysis.items():
            if columns:
                summary[seg_type] = {
                    'count': len(columns),
                    'columns': [c['column'] for c in columns],
                    'total_unique': sum(c['unique_count'] for c in columns),
                    'total_null': sum(c['null_count'] for c in columns)
                }
        
        return summary
    
    def create_segmentation_visualization_data(self, df: pd.DataFrame, seg_type: str, value_col: str = None) -> Dict:
        seg_analysis = self.analyze_segmentation(df)
        seg_columns = [c['column'] for c in seg_analysis.get(seg_type, [])]
        
        if not seg_columns:
            return {'data': [], 'labels': []}
        
        viz_data = []
        for col in seg_columns[:5]:
            if col in df.columns:
                if df[col].dtype in ['object', 'category']:
                    counts = df[col].value_counts().head(10)
                    viz_data.append({
                        'column': col,
                        'categories': counts.index.tolist(),
                        'counts': counts.values.tolist()
                    })
                elif df[col].dtype in ['int64', 'float64'] and value_col:
                    if value_col in df.columns:
                        grouped = df.groupby(col)[value_col].agg(['mean', 'count']).reset_index()
                        grouped = grouped.sort_values('mean', ascending=False).head(10)
                        viz_data.append({
                            'column': col,
                            'segments': grouped[col].tolist(),
                            'values': grouped['mean'].tolist(),
                            'counts': grouped['count'].tolist()
                        })
        
        return {'data': viz_data, 'type': seg_type}
