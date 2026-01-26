import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso
from sklearn.svm import SVR, SVC
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

from config import *

class PredictionAgent:
    """
    Agent for predictive modeling with multiple algorithms:
    - Regression: Linear, Ridge, Lasso, Random Forest, Gradient Boosting, SVM, Neural Network
    - Classification: Logistic Regression, Random Forest, Gradient Boosting, SVM, Neural Network
    """
    
    def __init__(self):
        self.models_dir = MODELS_DIR
        os.makedirs(self.models_dir, exist_ok=True)
        self.scaler = StandardScaler()
        self.label_encoders = {}
    
    def prepare_features(self, df: pd.DataFrame, target_col: str, 
                        handle_categorical: bool = True) -> tuple:
        """Prepare features and target for modeling"""
        # Separate features and target
        X = df.drop(columns=[target_col])
        y = df[target_col]
        # Ensure y is a Series
        if isinstance(y, pd.DataFrame):
            y = y.squeeze()
        
        # Handle categorical variables
        if handle_categorical:
            X_processed = X.copy()
            for col in X_processed.select_dtypes(include=['object', 'category']).columns:
                le = LabelEncoder()
                X_processed[col] = le.fit_transform(X_processed[col].astype(str))
                self.label_encoders[col] = le
        
        # Handle missing values
        X_processed = X_processed.fillna(X_processed.median(numeric_only=True))
        
        # Select only numeric columns
        X_processed = X_processed.select_dtypes(include=[np.number])
        
        return X_processed, y
    
    def is_classification(self, y: pd.Series) -> bool:
        """Determine if target is classification or regression"""
        # Check if target is categorical or has few unique values
        unique_ratio = len(y.unique()) / len(y)
        return unique_ratio < 0.1 or y.dtype == 'object' or y.dtype.name == 'category'
    
    def train_regression_models(self, X: pd.DataFrame, y: pd.Series, 
                                test_size: float = TEST_SIZE) -> dict:
        """Train multiple regression models and compare performance (memory-safe)"""
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=RANDOM_STATE
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Memory-safe models with reduced complexity
        models = {
            'linear_regression': LinearRegression(),
            'ridge': Ridge(alpha=1.0),
            'lasso': Lasso(alpha=1.0),
            'random_forest': RandomForestRegressor(n_estimators=50, max_depth=10, random_state=RANDOM_STATE, n_jobs=2),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=50, max_depth=5, random_state=RANDOM_STATE),
            'svr': SVR(kernel='rbf', cache_size=200),  # Limit cache
            'neural_network': MLPRegressor(hidden_layer_sizes=(50, 25), max_iter=300, random_state=RANDOM_STATE)
        }
        
        results = {}
        
        print(f"\n  Training {len(models)} regression models...")
        for idx, (name, model) in enumerate(models.items(), 1):
            try:
                print(f"  [{idx}/{len(models)}] Training {name}...", end=' ', flush=True)
                # Use scaled data for models that need it
                if name in ['linear_regression', 'ridge', 'lasso', 'svr', 'neural_network']:
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                print("✓", flush=True)
                
                # Calculate metrics
                mse = mean_squared_error(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                rmse = np.sqrt(mse)
                
                # Cross-validation score (reduced folds for memory)
                print(f"    Computing cross-validation...", end=' ', flush=True)
                cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring='r2', n_jobs=1)
                print("✓", flush=True)
                
                results[name] = {
                    'model': model,
                    'mse': mse,
                    'mae': mae,
                    'rmse': rmse,
                    'r2': r2,
                    'cv_mean': cv_scores.mean(),
                    'cv_std': cv_scores.std(),
                    'predictions': y_pred,
                    'actual': y_test.values
                }
                
                # Save model
                model_path = os.path.join(self.models_dir, f'{name}_regression.pkl')
                joblib.dump(model, model_path)
                results[name]['model_path'] = model_path
                
            except Exception as e:
                results[name] = {'error': str(e)}
        
        return results
    
    def train_classification_models(self, X: pd.DataFrame, y: pd.Series,
                                   test_size: float = TEST_SIZE) -> dict:
        """Train multiple classification models and compare performance (memory-safe)"""
        # Encode target if needed
        if y.dtype == 'object' or y.dtype.name == 'category':
            le_target = LabelEncoder()
            y_encoded = le_target.fit_transform(y)
            self.target_encoder = le_target
        else:
            y_encoded = y
            self.target_encoder = None
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=RANDOM_STATE
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Memory-safe models with reduced complexity
        models = {
            'logistic_regression': LogisticRegression(max_iter=500, random_state=RANDOM_STATE),
            'random_forest': RandomForestClassifier(n_estimators=50, max_depth=10, random_state=RANDOM_STATE, n_jobs=2),
            'gradient_boosting': GradientBoostingClassifier(n_estimators=50, max_depth=5, random_state=RANDOM_STATE),
            'svm': SVC(kernel='rbf', random_state=RANDOM_STATE, cache_size=200),  # Limit cache
            'neural_network': MLPClassifier(hidden_layer_sizes=(50, 25), max_iter=300, random_state=RANDOM_STATE)
        }
        
        results = {}
        
        print(f"\n  Training {len(models)} classification models...")
        for idx, (name, model) in enumerate(models.items(), 1):
            try:
                print(f"  [{idx}/{len(models)}] Training {name}...", end=' ', flush=True)
                # Use scaled data for models that need it
                if name in ['logistic_regression', 'svm', 'neural_network']:
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                print("✓", flush=True)
                
                # Calculate metrics
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
                recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
                f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
                
                # Cross-validation score (reduced folds for memory)
                print(f"    Computing cross-validation...", end=' ', flush=True)
                cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring='accuracy', n_jobs=1)
                print("✓", flush=True)
                
                results[name] = {
                    'model': model,
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1': f1,
                    'cv_mean': cv_scores.mean(),
                    'cv_std': cv_scores.std(),
                    'predictions': y_pred,
                    'actual': y_test,
                    'confusion_matrix': confusion_matrix(y_test, y_pred),
                    'classification_report': classification_report(y_test, y_pred)
                }
                
                # Save model
                model_path = os.path.join(self.models_dir, f'{name}_classification.pkl')
                joblib.dump(model, model_path)
                results[name]['model_path'] = model_path
                
            except Exception as e:
                results[name] = {'error': str(e)}
                print(f"✗ Error: {str(e)}", flush=True)
        
        return results
    
    def auto_train(self, df: pd.DataFrame, target_col: str) -> dict:
        """Automatically determine task type and train appropriate models
        Includes memory-safe sampling and feature limiting
        """
        # Memory-safe sampling: limit rows to prevent OOM
        MAX_TRAIN_ROWS = 50000
        if len(df) > MAX_TRAIN_ROWS:
            print(f"⚠ Sampling {MAX_TRAIN_ROWS} rows from {len(df)} for model training (memory optimization)")
            import sys
            sys.stdout.flush()
            df = df.sample(n=MAX_TRAIN_ROWS, random_state=RANDOM_STATE).reset_index(drop=True)
        
        print("  Preparing features...", end=' ', flush=True)
        X, y = self.prepare_features(df, target_col)
        print("✓", flush=True)
        
        # Limit features to prevent OOM
        MAX_FEATURES = 300
        if X.shape[1] > MAX_FEATURES:
            print(f"⚠ Limiting to top {MAX_FEATURES} features (out of {X.shape[1]}) for model training")
            import sys
            sys.stdout.flush()
            # Select top features by variance (most informative)
            feature_variance = X.var().sort_values(ascending=False)
            top_features = feature_variance.head(MAX_FEATURES).index.tolist()
            X = X[top_features]
        
        # Convert to float32 to reduce memory usage
        print("  Converting data types...", end=' ', flush=True)
        X = X.astype('float32')
        # Ensure y is a Series, not DataFrame
        if isinstance(y, pd.DataFrame):
            y = y.iloc[:, 0] if y.shape[1] > 0 else y.squeeze()
        if hasattr(y, 'dtype') and y.dtype in [np.float64, np.int64]:
            y = y.astype('float32' if not self.is_classification(y) else 'int32')
        print("✓", flush=True)
        
        # Determine task type
        print("  Determining task type...", end=' ', flush=True)
        is_classification = self.is_classification(y)
        task_type_str = 'classification' if is_classification else 'regression'
        print(f"✓ ({task_type_str})", flush=True)
        
        if is_classification:
            results = self.train_classification_models(X, y)
            results['task_type'] = 'classification'
        else:
            results = self.train_regression_models(X, y)
            results['task_type'] = 'regression'
        
        # Find best model
        if results['task_type'] == 'classification':
            best_model = max(
                [k for k in results.keys() if k != 'task_type'],
                key=lambda x: results[x].get('accuracy', 0) if 'accuracy' in results[x] else 0
            )
        else:
            best_model = max(
                [k for k in results.keys() if k != 'task_type'],
                key=lambda x: results[x].get('r2', -np.inf) if 'r2' in results[x] else -np.inf
            )
        
        results['best_model'] = best_model
        
        return results
    
    def hyperparameter_tuning(self, X: pd.DataFrame, y: pd.Series, 
                             model_name: str, task_type: str = 'auto') -> dict:
        """Perform hyperparameter tuning using GridSearchCV (memory-safe)"""
        if task_type == 'auto':
            task_type = 'classification' if self.is_classification(y) else 'regression'
        
        # Reduced parameter grids for memory efficiency
        param_grids = {
            'random_forest_regression': {
                'n_estimators': [50, 100],
                'max_depth': [10, 15],
                'min_samples_split': [2, 5]
            },
            'random_forest_classification': {
                'n_estimators': [50, 100],
                'max_depth': [10, 15],
                'min_samples_split': [2, 5]
            },
            'gradient_boosting_regression': {
                'n_estimators': [50, 100],
                'learning_rate': [0.1, 0.2],
                'max_depth': [3, 5]
            },
            'gradient_boosting_classification': {
                'n_estimators': [50, 100],
                'learning_rate': [0.1, 0.2],
                'max_depth': [3, 5]
            }
        }
        
        key = f"{model_name}_{task_type}"
        if key not in param_grids:
            return {'error': f'Hyperparameter tuning not available for {key}'}
        
        # Select base model
        if task_type == 'classification':
            if model_name == 'random_forest':
                base_model = RandomForestClassifier(random_state=RANDOM_STATE)
                scoring = 'accuracy'
            elif model_name == 'gradient_boosting':
                base_model = GradientBoostingClassifier(random_state=RANDOM_STATE)
                scoring = 'accuracy'
            else:
                return {'error': f'Hyperparameter tuning not available for {model_name} in classification'}
        else:
            if model_name == 'random_forest':
                base_model = RandomForestRegressor(random_state=RANDOM_STATE)
                scoring = 'r2'
            elif model_name == 'gradient_boosting':
                base_model = GradientBoostingRegressor(random_state=RANDOM_STATE)
                scoring = 'r2'
            else:
                return {'error': f'Hyperparameter tuning not available for {model_name} in regression'}
        
        # Grid search with reduced CV for memory
        grid_search = GridSearchCV(
            base_model,
            param_grids[key],
            cv=3,  # Reduced from 5
            scoring=scoring,
            n_jobs=1,  # Reduced parallelism
            verbose=0
        )
        
        grid_search.fit(X, y)
        
        # Save best model
        model_path = os.path.join(self.models_dir, f'{model_name}_tuned_{task_type}.pkl')
        joblib.dump(grid_search.best_estimator_, model_path)
        
        return {
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_,
            'best_model': grid_search.best_estimator_,
            'model_path': model_path
        }
    
    def predict(self, model_path: str, X: pd.DataFrame) -> np.ndarray:
        """Make predictions using a saved model"""
        model = joblib.load(model_path)
        
        # Scale if needed
        if hasattr(self, 'scaler') and self.scaler is not None:
            X_scaled = self.scaler.transform(X)
            return model.predict(X_scaled)
        else:
            return model.predict(X)
