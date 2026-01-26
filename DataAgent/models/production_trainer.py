"""
Production-Grade Model Trainer
Trains all models (forecasting, prediction, classification, recommendation) 
and saves them with proper naming conventions
Works with any CSV/Excel data
"""
import pandas as pd
import numpy as np
import os
from typing import Dict, Any, Optional, Union
import warnings
warnings.filterwarnings('ignore')

from config import *
from models.model_manager import ModelManager
from models.model_factory import ModelFactory
from agents.forecastingAgent import ForecastingAgent
from agents.predictionAgent import PredictionAgent
from utils.data_loader import UniversalDataLoader


class ProductionModelTrainer:
    """
    Production-grade trainer that trains and saves all model types
    """
    
    def __init__(self):
        self.model_manager = ModelManager()
        self.model_factory = ModelFactory()
        self.forecaster = ForecastingAgent()
        self.predictor = PredictionAgent()
        self.data_loader = UniversalDataLoader()
    
    def train_all_models(self, data_path: Union[str, pd.DataFrame],
                        target_col: Optional[str] = None,
                        date_col: Optional[str] = None,
                        value_col: Optional[str] = None,
                        forecast_periods: int = 30) -> Dict[str, Any]:
        """
        Train all models on the provided data
        
        Args:
            data_path: Path to CSV/Excel file or DataFrame
            target_col: Target column for prediction/classification
            date_col: Date column for forecasting
            value_col: Value column for forecasting
            forecast_periods: Number of periods to forecast
        
        Returns:
            Dictionary with training results for all models
        """
        results = {
            'forecasting_models': {},
            'prediction_models': {},
            'classification_models': {},
            'recommendation_models': {}
        }
        
        # Load data
        if isinstance(data_path, str):
            print(f"Loading data from: {data_path}")
            df = self.data_loader.load(data_path)
            print(f"✓ Loaded {len(df)} rows × {len(df.columns)} columns")
        else:
            df = data_path
        
        # Train forecasting models if date and value columns provided
        if date_col and value_col:
            print("\n[1/4] Training Forecasting Models...")
            try:
                ts = self.forecaster.prepare_time_series(df, date_col, value_col)
                forecast_results = self.forecaster.compare_forecasts(ts, forecast_periods)
                results['forecasting_models'] = forecast_results
                print("✓ Forecasting models trained and saved")
            except Exception as e:
                print(f"⚠ Forecasting models error: {e}")
                results['forecasting_models'] = {'error': str(e)}
        
        # Train prediction/classification models if target column provided
        if target_col:
            print("\n[2/4] Training Prediction/Classification Models...")
            try:
                prediction_results = self.predictor.auto_train(df, target_col)
                results['prediction_models'] = prediction_results
                
                # Extract and save Random Forest models separately
                if 'random_forest' in prediction_results:
                    rf_result = prediction_results['random_forest']
                    if 'model' in rf_result:
                        task_type = prediction_results.get('task_type', 'regression')
                        self.model_manager.save_prediction_model(
                            rf_result['model'],
                            'random_forest',
                            task_type,
                            metadata={
                                'r2': rf_result.get('r2', 0) if task_type == 'regression' else None,
                                'accuracy': rf_result.get('accuracy', 0) if task_type == 'classification' else None
                            }
                        )
                
                print("✓ Prediction/Classification models trained and saved")
            except Exception as e:
                print(f"⚠ Prediction models error: {e}")
                results['prediction_models'] = {'error': str(e)}
        
        # Train MCP classification models
        print("\n[3/4] Training MCP Classification Models...")
        try:
            classification_results = self._train_mcp_classification_models(df, target_col)
            results['classification_models'] = classification_results
            print("✓ MCP Classification models trained and saved")
        except Exception as e:
            print(f"⚠ Classification models error: {e}")
            results['classification_models'] = {'error': str(e)}
        
        # Train MCP recommendation models (if applicable)
        print("\n[4/4] Training MCP Recommendation Models...")
        try:
            recommendation_results = self._train_mcp_recommendation_models(df)
            results['recommendation_models'] = recommendation_results
            print("✓ MCP Recommendation models trained and saved")
        except Exception as e:
            print(f"⚠ Recommendation models error: {e}")
            results['recommendation_models'] = {'error': str(e)}
        
        return results
    
    def _train_mcp_classification_models(self, df: pd.DataFrame, target_col: str) -> Dict:
        """Train all MCP classification models"""
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import LabelEncoder
        from sklearn.metrics import accuracy_score
        
        results = {}
        
        # Prepare data
        X, y = self.predictor.prepare_features(df, target_col)
        
        # Limit features for memory safety
        MAX_FEATURES = 300
        if X.shape[1] > MAX_FEATURES:
            feature_variance = X.var().sort_values(ascending=False)
            top_features = feature_variance.head(MAX_FEATURES).index.tolist()
            X = X[top_features]
        
        # Encode target if needed
        if y.dtype == 'object' or y.dtype.name == 'category':
            le = LabelEncoder()
            y_encoded = le.fit_transform(y)
        else:
            y_encoded = y
            le = None
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=TEST_SIZE, random_state=RANDOM_STATE
        )
        
        # Get available classification models
        available_models = self.model_factory.get_available_models('classification')
        
        # Train each model
        for model_name in available_models[:5]:  # Limit to top 5 for memory
            try:
                # Create and train model
                context = self.model_factory.create_classification_model(model_name)
                context.model.fit(X_train, y_train)
                
                # Evaluate
                y_pred = context.model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                
                # Save model
                model_path = self.model_manager.save_classification_model(
                    context.model,
                    model_name,
                    metadata={'accuracy': float(accuracy)}
                )
                
                results[model_name] = {
                    'accuracy': accuracy,
                    'model_path': model_path,
                    'context': context
                }
                
            except Exception as e:
                results[model_name] = {'error': str(e)}
        
        return results
    
    def _train_mcp_recommendation_models(self, df: pd.DataFrame) -> Dict:
        """Train MCP recommendation models (if data structure supports it)"""
        results = {}
        
        # Check if data has user-item interaction structure
        # Look for columns that might indicate user-item interactions
        potential_user_cols = [col for col in df.columns if 'user' in col.lower() or 'id' in col.lower()]
        potential_item_cols = [col for col in df.columns if 'item' in col.lower() or 'product' in col.lower()]
        potential_rating_cols = [col for col in df.columns if 'rating' in col.lower() or 'score' in col.lower()]
        
        if len(potential_user_cols) >= 1 and len(potential_item_cols) >= 1:
            try:
                user_col = potential_user_cols[0]
                item_col = potential_item_cols[0]
                rating_col = potential_rating_cols[0] if potential_rating_cols else df.select_dtypes(include=[np.number]).columns[0]
                
                # Create interactions dataframe
                interactions = df[[user_col, item_col, rating_col]].copy()
                interactions.columns = ['user_id', 'item_id', 'rating']
                
                # Get available recommendation models
                available_models = self.model_factory.get_available_models('recommendation')
                
                # Train each model
                for model_name in available_models[:2]:  # Limit for memory
                    try:
                        context = self.model_factory.create_recommendation_model(model_name)
                        context.model.fit(interactions)
                        
                        # Save model
                        model_path = self.model_manager.save_recommendation_model(
                            context.model,
                            model_name,
                            metadata={'n_interactions': len(interactions)}
                        )
                        
                        results[model_name] = {
                            'model_path': model_path,
                            'context': context
                        }
                    except Exception as e:
                        results[model_name] = {'error': str(e)}
            except Exception as e:
                results['error'] = f"Could not train recommendation models: {str(e)}"
        else:
            results['info'] = "Data structure not suitable for recommendation models (requires user-item interactions)"
        
        return results
    
    def list_trained_models(self) -> Dict:
        """List all trained models"""
        return self.model_manager.list_saved_models()
    
    def load_model(self, model_path: str):
        """Load a trained model"""
        return self.model_manager.load_model(model_path)
