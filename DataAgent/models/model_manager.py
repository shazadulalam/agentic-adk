"""
Production-Grade Model Manager
Handles saving, loading, and managing all ML models for the DataAgent platform
Works with any CSV/Excel data
"""
import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Optional dependencies
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

from config import MODELS_DIR


class ModelManager:
    """
    Production-grade model manager for saving, loading, and managing ML models
    Supports:
    - Forecasting models: ARIMA, Prophet, LSTM
    - Prediction models: Random Forest, Linear Regression, etc.
    - Classification models: All MCP classification models
    - Recommendation models: All MCP recommendation models
    """
    
    def __init__(self, models_dir: str = None):
        """
        Initialize Model Manager
        
        Args:
            models_dir: Directory to save/load models (default: MODELS_DIR from config)
        """
        self.models_dir = models_dir or MODELS_DIR
        os.makedirs(self.models_dir, exist_ok=True)
        self.metadata_file = os.path.join(self.models_dir, 'model_metadata.json')
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load model metadata from file"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_metadata(self):
        """Save model metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save metadata: {e}")
    
    def save_forecasting_model(self, model: Any, model_type: str, 
                               metadata: Dict = None) -> str:
        """
        Save forecasting model (ARIMA, Prophet, or LSTM)
        
        Args:
            model: The trained model
            model_type: 'arima', 'prophet', or 'lstm'
            metadata: Additional metadata to store
        
        Returns:
            Path to saved model
        """
        model_type = model_type.lower()
        
        if model_type == 'arima':
            model_path = os.path.join(self.models_dir, 'arima_model.pkl')
            joblib.dump(model, model_path)
            
        elif model_type == 'prophet':
            model_path = os.path.join(self.models_dir, 'prophet_model.pkl')
            joblib.dump(model, model_path)
            
        elif model_type == 'lstm':
            if not TENSORFLOW_AVAILABLE:
                raise ImportError("TensorFlow is required for LSTM models")
            model_path = os.path.join(self.models_dir, 'lstm_model.h5')
            model.save(model_path)
            
        else:
            raise ValueError(f"Unknown forecasting model type: {model_type}")
        
        # Save metadata
        self.metadata[model_type] = {
            'model_path': model_path,
            'model_type': model_type,
            'saved_at': datetime.now().isoformat(),
            **(metadata or {})
        }
        self._save_metadata()
        
        return model_path
    
    def save_prediction_model(self, model: Any, model_name: str, 
                             task_type: str = 'regression',
                             metadata: Dict = None) -> str:
        """
        Save prediction model (Random Forest, Linear Regression, etc.)
        
        Args:
            model: The trained model
            model_name: Name of the model (e.g., 'random_forest', 'linear_regression')
            task_type: 'regression' or 'classification'
            metadata: Additional metadata to store
        
        Returns:
            Path to saved model
        """
        # Generate filename based on naming convention
        if 'random_forest' in model_name.lower():
            # Random Forest models: random_forest_*.pkl
            if task_type == 'regression':
                filename = f'random_forest_regression.pkl'
            else:
                filename = f'random_forest_classification.pkl'
        else:
            # Other models: {model_name}_{task_type}.pkl
            filename = f'{model_name}_{task_type}.pkl'
        
        model_path = os.path.join(self.models_dir, filename)
        joblib.dump(model, model_path)
        
        # Save metadata
        key = f"{model_name}_{task_type}"
        self.metadata[key] = {
            'model_path': model_path,
            'model_name': model_name,
            'task_type': task_type,
            'saved_at': datetime.now().isoformat(),
            **(metadata or {})
        }
        self._save_metadata()
        
        return model_path
    
    def save_classification_model(self, model: Any, model_name: str,
                                  metadata: Dict = None) -> str:
        """
        Save MCP classification model
        
        Args:
            model: The trained classification model
            model_name: Name of the model (e.g., 'logistic_regression', 'random_forest')
            metadata: Additional metadata to store
        
        Returns:
            Path to saved model
        """
        filename = f'{model_name}_classification.pkl'
        model_path = os.path.join(self.models_dir, filename)
        joblib.dump(model, model_path)
        
        # Save metadata
        key = f"{model_name}_classification"
        self.metadata[key] = {
            'model_path': model_path,
            'model_name': model_name,
            'model_type': 'classification',
            'saved_at': datetime.now().isoformat(),
            **(metadata or {})
        }
        self._save_metadata()
        
        return model_path
    
    def save_recommendation_model(self, model: Any, model_name: str,
                                  metadata: Dict = None) -> str:
        """
        Save MCP recommendation model
        
        Args:
            model: The trained recommendation model
            model_name: Name of the model (e.g., 'collaborative_filtering', 'matrix_factorization')
            metadata: Additional metadata to store
        
        Returns:
            Path to saved model
        """
        filename = f'{model_name}_recommendation.pkl'
        model_path = os.path.join(self.models_dir, filename)
        joblib.dump(model, model_path)
        
        # Save metadata
        key = f"{model_name}_recommendation"
        self.metadata[key] = {
            'model_path': model_path,
            'model_name': model_name,
            'model_type': 'recommendation',
            'saved_at': datetime.now().isoformat(),
            **(metadata or {})
        }
        self._save_metadata()
        
        return model_path
    
    def load_model(self, model_path: str) -> Any:
        """
        Load a saved model
        
        Args:
            model_path: Path to the model file
        
        Returns:
            Loaded model
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        # Check if it's a TensorFlow model
        if model_path.endswith('.h5'):
            if not TENSORFLOW_AVAILABLE:
                raise ImportError("TensorFlow is required to load LSTM models")
            return tf.keras.models.load_model(model_path)
        else:
            return joblib.load(model_path)
    
    def load_forecasting_model(self, model_type: str) -> Any:
        """Load a forecasting model by type"""
        model_type = model_type.lower()
        
        if model_type == 'arima':
            model_path = os.path.join(self.models_dir, 'arima_model.pkl')
        elif model_type == 'prophet':
            model_path = os.path.join(self.models_dir, 'prophet_model.pkl')
        elif model_type == 'lstm':
            model_path = os.path.join(self.models_dir, 'lstm_model.h5')
        else:
            raise ValueError(f"Unknown forecasting model type: {model_type}")
        
        return self.load_model(model_path)
    
    def list_saved_models(self) -> Dict[str, Dict]:
        """List all saved models with their metadata"""
        return self.metadata.copy()
    
    def get_model_info(self, model_key: str) -> Dict:
        """Get information about a specific model"""
        return self.metadata.get(model_key, {})
    
    def delete_model(self, model_path: str):
        """Delete a model file and its metadata"""
        if os.path.exists(model_path):
            os.remove(model_path)
        
        # Remove from metadata
        for key, info in list(self.metadata.items()):
            if info.get('model_path') == model_path:
                del self.metadata[key]
        
        self._save_metadata()
    
    def model_exists(self, model_type: str, model_name: str = None) -> bool:
        """Check if a model exists"""
        if model_type in ['arima', 'prophet', 'lstm']:
            if model_type == 'arima':
                path = os.path.join(self.models_dir, 'arima_model.pkl')
            elif model_type == 'prophet':
                path = os.path.join(self.models_dir, 'prophet_model.pkl')
            else:  # lstm
                path = os.path.join(self.models_dir, 'lstm_model.h5')
            return os.path.exists(path)
        else:
            # Search in metadata
            for key, info in self.metadata.items():
                if model_name and info.get('model_name') == model_name:
                    return os.path.exists(info.get('model_path', ''))
            return False
