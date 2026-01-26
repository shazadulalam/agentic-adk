"""
Universal Data Loader for CSV and Excel Files
Production-grade data loading with automatic format detection
"""
import pandas as pd
import numpy as np
import os
from typing import Union, Optional, Dict, Any
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class UniversalDataLoader:
    """
    Universal data loader that works with any CSV or Excel file
    Handles various formats, encodings, and edge cases
    """
    
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls', '.xlsm', '.xlsb']
    
    def load(self, file_path: Union[str, Path], 
             sheet_name: Optional[Union[str, int, list]] = None,
             **kwargs) -> pd.DataFrame:
        """
        Load data from CSV or Excel file
        
        Args:
            file_path: Path to the data file
            sheet_name: For Excel files, specify sheet name or index (default: first sheet)
            **kwargs: Additional arguments passed to pd.read_csv or pd.read_excel
        
        Returns:
            Loaded DataFrame
        """
        file_path = str(file_path)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext not in self.supported_formats:
            raise ValueError(
                f"Unsupported file format: {file_ext}. "
                f"Supported formats: {', '.join(self.supported_formats)}"
            )
        
        # Default kwargs for better compatibility
        default_kwargs = {}
        if file_ext == '.csv':
            # Don't use 'python' engine with low_memory
            if 'engine' not in kwargs:
                default_kwargs['engine'] = 'c'  # Use C engine by default
        default_kwargs.update(kwargs)
        
        try:
            if file_ext == '.csv':
                return self._load_csv(file_path, **default_kwargs)
            else:
                return self._load_excel(file_path, sheet_name=sheet_name, **default_kwargs)
        except Exception as e:
            # Try with different encodings for CSV
            if file_ext == '.csv':
                return self._load_csv_with_encoding_fallback(file_path, **default_kwargs)
            else:
                raise e
    
    def _load_csv(self, file_path: str, **kwargs) -> pd.DataFrame:
        """Load CSV file with automatic encoding detection"""
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding, **kwargs)
                return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                # If it's not an encoding error, try next encoding
                if 'codec' not in str(e).lower() and 'decode' not in str(e).lower():
                    raise e
        
        # If all encodings fail, try with error handling
        kwargs_no_errors = {k: v for k, v in kwargs.items() if k != 'errors'}
        return pd.read_csv(file_path, encoding='utf-8', **kwargs_no_errors)
    
    def _load_csv_with_encoding_fallback(self, file_path: str, **kwargs) -> pd.DataFrame:
        """Fallback CSV loading with error handling"""
        try:
            # Try with different separators
            separators = [',', ';', '\t', '|']
            for sep in separators:
                try:
                    df = pd.read_csv(file_path, sep=sep, encoding='utf-8', errors='ignore', **kwargs)
                    if df.shape[1] > 1:  # Valid separator
                        return df
                except:
                    continue
        except:
            pass
        
        # Last resort: read with error handling
        kwargs_no_errors = {k: v for k, v in kwargs.items() if k != 'errors'}
        return pd.read_csv(file_path, encoding='utf-8', **kwargs_no_errors)
    
    def _load_excel(self, file_path: str, sheet_name: Optional[Union[str, int, list]] = None, **kwargs) -> pd.DataFrame:
        """Load Excel file"""
        try:
            if sheet_name is None:
                # Load first sheet by default
                df = pd.read_excel(file_path, sheet_name=0, **kwargs)
            else:
                df = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
            
            # If multiple sheets, return first one
            if isinstance(df, dict):
                df = list(df.values())[0]
            
            return df
        except Exception as e:
            # Try with openpyxl engine
            try:
                if sheet_name is None:
                    df = pd.read_excel(file_path, sheet_name=0, engine='openpyxl', **kwargs)
                else:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl', **kwargs)
                
                if isinstance(df, dict):
                    df = list(df.values())[0]
                
                return df
            except:
                raise e
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate loaded data and return statistics
        
        Args:
            df: DataFrame to validate
        
        Returns:
            Dictionary with validation results
        """
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'missing_values': df.isnull().sum().to_dict(),
            'dtypes': df.dtypes.to_dict(),
            'numeric_columns': list(df.select_dtypes(include=[np.number]).columns),
            'categorical_columns': list(df.select_dtypes(include=['object', 'category']).columns),
            'date_columns': self._detect_date_columns(df),
            'duplicate_rows': df.duplicated().sum()
        }
    
    def _detect_date_columns(self, df: pd.DataFrame) -> list:
        """Detect columns that might be dates"""
        date_cols = []
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    pd.to_datetime(df[col].dropna().iloc[0:10])
                    date_cols.append(col)
                except:
                    pass
        return date_cols
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Get information about a data file without loading it"""
        file_path = str(file_path)
        stat = os.stat(file_path)
        
        return {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_size_mb': stat.st_size / 1024**2,
            'file_extension': Path(file_path).suffix.lower(),
            'is_supported': Path(file_path).suffix.lower() in self.supported_formats
        }
