"""
Model Context Protocol - Context management for models
"""
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import joblib
import os
from config import MODELS_DIR


class ModelContext:
    """
    Context object that holds model state, configuration, and metadata
    Implements Model Context Protocol pattern
    """
    
    def __init__(self, model_name: str, model_type: str, config: Dict[str, Any] = None):
        self.model_name = model_name
        self.model_type = model_type  # 'classification', 'regression', 'recommendation', 'forecasting'
        self.config = config or {}
        self.model = None
        self.metadata = {
            'created_at': None,
            'trained': False,
            'metrics': {},
            'feature_names': [],
            'target_name': None
        }
        self.model_path = None
    
    def set_model(self, model: Any):
        """Set the model instance"""
        self.model = model
        self.metadata['trained'] = True
    
    def set_metadata(self, key: str, value: Any):
        """Set metadata value"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        return self.metadata.get(key, default)
    
    def set_metrics(self, metrics: Dict[str, float]):
        """Set model performance metrics"""
        self.metadata['metrics'] = metrics
    
    def set_features(self, feature_names: list):
        """Set feature names"""
        self.metadata['feature_names'] = feature_names
    
    def set_target(self, target_name: str):
        """Set target name"""
        self.metadata['target_name'] = target_name
    
    def save(self, path: Optional[str] = None):
        """Save model and context to disk"""
        if path is None:
            os.makedirs(MODELS_DIR, exist_ok=True)
            path = os.path.join(MODELS_DIR, f"{self.model_name}_{self.model_type}.pkl")
        
        self.model_path = path
        
        # Save model
        if self.model is not None:
            joblib.dump({
                'model': self.model,
                'context': {
                    'model_name': self.model_name,
                    'model_type': self.model_type,
                    'config': self.config,
                    'metadata': self.metadata
                }
            }, path)
        
        return path
    
    def load(self, path: str):
        """Load model and context from disk"""
        data = joblib.load(path)
        self.model = data['model']
        context = data['context']
        self.model_name = context['model_name']
        self.model_type = context['model_type']
        self.config = context['config']
        self.metadata = context['metadata']
        self.model_path = path
        return self
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions using the model"""
        if self.model is None:
            raise ValueError("Model not loaded or trained")
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Get prediction probabilities (for classification)"""
        if self.model is None:
            raise ValueError("Model not loaded or trained")
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X)
        else:
            raise ValueError("Model does not support predict_proba")
    
    def get_info(self) -> Dict[str, Any]:
        """Get complete context information"""
        return {
            'model_name': self.model_name,
            'model_type': self.model_type,
            'config': self.config,
            'metadata': self.metadata,
            'model_path': self.model_path,
            'is_trained': self.metadata['trained']
        }
