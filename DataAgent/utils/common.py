import sys
import os
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def get_parent_path():
    """Get parent directory path"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def setup_path():
    """Setup sys.path for imports"""
    parent_dir = get_parent_path()
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    return parent_dir

def get_numeric_cols(df):
    """Get numeric columns from dataframe"""
    return df.select_dtypes(include=[np.number]).columns

def get_categorical_cols(df):
    """Get categorical columns from dataframe"""
    return df.select_dtypes(include=['object', 'category']).columns

def calc_missing_pct(df):
    """Calculate missing data percentage"""
    if df.shape[0] == 0 or df.shape[1] == 0:
        return 0
    return (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
