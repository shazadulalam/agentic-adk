"""
Model Factory - Creates models using Model Context Protocol
"""
from typing import Dict, Any, Optional
import pandas as pd
from .model_context import ModelContext
from .classification_models import ClassificationModelRegistry
from .recommendation_models import RecommendationModelRegistry


class ModelFactory:
    """
    Factory class for creating models using MCP pattern
    """
    
    def __init__(self):
        self.classification_registry = ClassificationModelRegistry()
        self.recommendation_registry = RecommendationModelRegistry()
    
    def create_classification_model(self, model_name: str, config: Dict[str, Any] = None) -> ModelContext:
        """Create a classification model"""
        context = ModelContext(model_name, 'classification', config)
        model = self.classification_registry.get_model(model_name, config)
        context.set_model(model)
        return context
    
    def create_recommendation_model(self, model_name: str, config: Dict[str, Any] = None) -> ModelContext:
        """Create a recommendation model"""
        context = ModelContext(model_name, 'recommendation', config)
        model = self.recommendation_registry.get_model(model_name, config)
        context.set_model(model)
        return context
    
    def train_classification_model(self, context: ModelContext, 
                                   X: pd.DataFrame, y: pd.Series) -> ModelContext:
        """Train a classification model"""
        context.model.fit(X, y)
        context.set_features(list(X.columns))
        if hasattr(y, 'name'):
            context.set_target(y.name)
        context.metadata['trained'] = True
        return context
    
    def train_recommendation_model(self, context: ModelContext, 
                                  interactions: pd.DataFrame) -> ModelContext:
        """Train a recommendation model"""
        context.model.fit(interactions)
        context.metadata['trained'] = True
        return context
    
    def get_available_models(self, model_type: str) -> list:
        """Get list of available models for a type"""
        if model_type == 'classification':
            return self.classification_registry.list_models()
        elif model_type == 'recommendation':
            return self.recommendation_registry.list_models()
        else:
            return []
