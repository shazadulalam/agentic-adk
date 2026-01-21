"""
Test Agent - Comprehensive testing for all agents and components
"""
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.cleanerAgent import Cleaner
from agents.analyzer import ModelAnalyzer
from agents.forecastingAgent import ForecastingAgent
from agents.predictionAgent import PredictionAgent
from agents.explorationAgent import ExplorationAgent
from models.model_factory import ModelFactory
from models.model_context import ModelContext
from config import *


class TestAgent:
    """
    Comprehensive test agent to verify all components work correctly
    """
    
    def __init__(self):
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
        self.test_data = None
    
    def generate_test_data(self, n_samples: int = 1000):
        """Generate synthetic test data"""
        np.random.seed(42)
        
        # Create time series data
        dates = pd.date_range(start='2020-01-01', periods=n_samples, freq='D')
        
        # Create classification dataset
        X_class = np.random.randn(n_samples, 5)
        y_class = (X_class[:, 0] + X_class[:, 1] > 0).astype(int)
        
        df_class = pd.DataFrame(X_class, columns=[f'feature_{i}' for i in range(5)])
        df_class['target'] = y_class
        df_class['date'] = dates[:n_samples]
        
        # Create regression dataset
        X_reg = np.random.randn(n_samples, 5)
        y_reg = X_reg[:, 0] * 2 + X_reg[:, 1] * 1.5 + np.random.randn(n_samples) * 0.5
        
        df_reg = pd.DataFrame(X_reg, columns=[f'feature_{i}' for i in range(5)])
        df_reg['target'] = y_reg
        
        # Create time series dataset
        trend = np.linspace(0, 10, n_samples)
        seasonal = 5 * np.sin(2 * np.pi * np.arange(n_samples) / 365.25)
        noise = np.random.randn(n_samples) * 0.5
        ts_values = trend + seasonal + noise
        
        df_ts = pd.DataFrame({
            'date': dates,
            'value': ts_values
        })
        
        # Create recommendation dataset
        n_users, n_items = 100, 50
        interactions = []
        for user_id in range(n_users):
            for item_id in np.random.choice(n_items, size=10, replace=False):
                interactions.append({
                    'user_id': user_id,
                    'item_id': item_id,
                    'rating': np.random.randint(1, 6)
                })
        
        df_rec = pd.DataFrame(interactions)
        
        self.test_data = {
            'classification': df_class,
            'regression': df_reg,
            'time_series': df_ts,
            'recommendation': df_rec
        }
        
        return self.test_data
    
    def test_cleaner_agent(self):
        """Test Cleaner Agent"""
        print("\n" + "="*60)
        print("Testing Cleaner Agent...")
        print("="*60)
        
        try:
            cleaner = Cleaner()
            
            # Test data cleaning
            df = self.test_data['classification'].copy()
            df.loc[0:10, 'feature_0'] = np.nan  # Add missing values
            df = pd.concat([df, df.head(5)])  # Add duplicates
            
            df_cleaned = cleaner.clean_data(df)
            
            assert len(df_cleaned) <= len(df), "Cleaning should remove duplicates"
            assert df_cleaned['feature_0'].isnull().sum() < df['feature_0'].isnull().sum(), "Should fill missing values"
            
            self.results['passed'].append("Cleaner Agent - Data Cleaning")
            print("✓ Cleaner Agent: Data cleaning works correctly")
            
        except Exception as e:
            self.results['failed'].append(f"Cleaner Agent: {str(e)}")
            print(f"✗ Cleaner Agent failed: {str(e)}")
    
    def test_analyzer_agent(self):
        """Test Analyzer Agent"""
        print("\n" + "="*60)
        print("Testing Analyzer Agent...")
        print("="*60)
        
        try:
            analyzer = ModelAnalyzer()
            df = self.test_data['classification']
            
            results = analyzer.analyze_and_plot(df, target_col='target')
            
            assert 'basic_stats' in results, "Should have basic stats"
            assert 'data_quality' in results, "Should have data quality report"
            assert 'distributions' in results, "Should have distribution analysis"
            assert os.path.exists(results['html_report']), "HTML report should be created"
            
            self.results['passed'].append("Analyzer Agent - EDA")
            print("✓ Analyzer Agent: EDA works correctly")
            
        except Exception as e:
            self.results['failed'].append(f"Analyzer Agent: {str(e)}")
            print(f"✗ Analyzer Agent failed: {str(e)}")
    
    def test_forecasting_agent(self):
        """Test Forecasting Agent"""
        print("\n" + "="*60)
        print("Testing Forecasting Agent...")
        print("="*60)
        
        try:
            forecaster = ForecastingAgent()
            df = self.test_data['time_series']
            
            ts = forecaster.prepare_time_series(df, 'date', 'value')
            
            # Test ARIMA
            arima_result = forecaster.forecast_arima(ts, forecast_periods=30)
            assert 'forecast' in arima_result, "ARIMA should return forecast"
            
            # Test Prophet
            prophet_result = forecaster.forecast_prophet(df, 'date', 'value', forecast_periods=30)
            assert 'forecast' in prophet_result, "Prophet should return forecast"
            
            self.results['passed'].append("Forecasting Agent - ARIMA")
            self.results['passed'].append("Forecasting Agent - Prophet")
            print("✓ Forecasting Agent: ARIMA and Prophet work correctly")
            
        except Exception as e:
            self.results['failed'].append(f"Forecasting Agent: {str(e)}")
            print(f"✗ Forecasting Agent failed: {str(e)}")
    
    def test_prediction_agent(self):
        """Test Prediction Agent"""
        print("\n" + "="*60)
        print("Testing Prediction Agent...")
        print("="*60)
        
        try:
            predictor = PredictionAgent()
            
            # Test classification
            df_class = self.test_data['classification']
            class_results = predictor.train_classification_models(
                df_class.drop(columns=['target', 'date']), 
                df_class['target']
            )
            assert len(class_results) > 0, "Should train multiple models"
            assert 'random_forest' in class_results, "Should include random forest"
            
            # Test regression
            df_reg = self.test_data['regression']
            reg_results = predictor.train_regression_models(
                df_reg.drop(columns=['target']),
                df_reg['target']
            )
            assert len(reg_results) > 0, "Should train multiple models"
            
            self.results['passed'].append("Prediction Agent - Classification")
            self.results['passed'].append("Prediction Agent - Regression")
            print("✓ Prediction Agent: Classification and Regression work correctly")
            
        except Exception as e:
            self.results['failed'].append(f"Prediction Agent: {str(e)}")
            print(f"✗ Prediction Agent failed: {str(e)}")
    
    def test_exploration_agent(self):
        """Test Exploration Agent"""
        print("\n" + "="*60)
        print("Testing Exploration Agent...")
        print("="*60)
        
        try:
            explorer = ExplorationAgent()
            df = self.test_data['classification']
            
            # Test feature engineering
            df_engineered = explorer.feature_engineering(df)
            assert df_engineered.shape[1] >= df.shape[1], "Should add features"
            
            # Test insights
            insights = explorer.generate_insights(df, target_col='target')
            assert 'data_quality' in insights, "Should have data quality insights"
            assert 'recommendations' in insights, "Should have recommendations"
            
            self.results['passed'].append("Exploration Agent - Feature Engineering")
            self.results['passed'].append("Exploration Agent - Insights")
            print("✓ Exploration Agent: Feature engineering and insights work correctly")
            
        except Exception as e:
            self.results['failed'].append(f"Exploration Agent: {str(e)}")
            print(f"✗ Exploration Agent failed: {str(e)}")
    
    def test_mcp_classification_models(self):
        """Test MCP Classification Models"""
        print("\n" + "="*60)
        print("Testing MCP Classification Models...")
        print("="*60)
        
        try:
            factory = ModelFactory()
            df = self.test_data['classification']
            X = df.drop(columns=['target', 'date'])
            y = df['target']
            
            # Test multiple classification models
            model_names = ['logistic_regression', 'random_forest', 'gradient_boosting', 'svm']
            
            for model_name in model_names:
                context = factory.create_classification_model(model_name)
                context = factory.train_classification_model(context, X, y)
                
                # Test prediction
                predictions = context.predict(X.head(10))
                assert len(predictions) == 10, f"{model_name} should make predictions"
                
                # Test saving
                model_path = context.save()
                assert os.path.exists(model_path), f"{model_name} should save correctly"
                
                # Test loading
                loaded_context = ModelContext(model_name, 'classification').load(model_path)
                assert loaded_context.model is not None, f"{model_name} should load correctly"
                
                self.results['passed'].append(f"MCP - {model_name}")
            
            print("✓ MCP Classification Models work correctly")
            
        except Exception as e:
            self.results['failed'].append(f"MCP Classification: {str(e)}")
            print(f"✗ MCP Classification failed: {str(e)}")
    
    def test_mcp_recommendation_models(self):
        """Test MCP Recommendation Models"""
        print("\n" + "="*60)
        print("Testing MCP Recommendation Models...")
        print("="*60)
        
        try:
            factory = ModelFactory()
            df = self.test_data['recommendation']
            
            # Test collaborative filtering
            context = factory.create_recommendation_model('collaborative_filtering')
            context = factory.train_recommendation_model(context, df)
            
            # Test recommendations
            recommendations = context.model.recommend_items(user_id=0, n_recommendations=5)
            assert len(recommendations) > 0, "Should generate recommendations"
            
            self.results['passed'].append("MCP - Collaborative Filtering")
            
            # Test matrix factorization
            context_mf = factory.create_recommendation_model('matrix_factorization')
            context_mf = factory.train_recommendation_model(context_mf, df)
            recommendations_mf = context_mf.model.recommend_items(user_id=0, n_recommendations=5)
            assert len(recommendations_mf) > 0, "Matrix factorization should generate recommendations"
            
            self.results['passed'].append("MCP - Matrix Factorization")
            
            print("✓ MCP Recommendation Models work correctly")
            
        except Exception as e:
            self.results['failed'].append(f"MCP Recommendation: {str(e)}")
            print(f"✗ MCP Recommendation failed: {str(e)}")
    
    def test_views(self):
        """Test View Components"""
        print("\n" + "="*60)
        print("Testing Views...")
        print("="*60)
        
        try:
            from views.eda_report_view import EDAReportView
            from views.dashboard_views import OverviewTabView
            
            df = self.test_data['classification']
            
            # Test EDA report view
            analyzer = ModelAnalyzer()
            results = analyzer.analyze_and_plot(df, target_col='target')
            report_path = EDAReportView.generate_html_report(df, results)
            assert os.path.exists(report_path), "EDA report view should create HTML"
            
            # Test dashboard views
            overview = OverviewTabView.render(df)
            assert overview is not None, "Overview view should render"
            
            self.results['passed'].append("Views - EDA Report")
            self.results['passed'].append("Views - Dashboard")
            print("✓ Views work correctly")
            
        except Exception as e:
            self.results['failed'].append(f"Views: {str(e)}")
            print(f"✗ Views failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("DataAgent - Comprehensive Test Suite")
        print("="*60)
        
        # Generate test data
        print("\nGenerating test data...")
        self.generate_test_data()
        print("✓ Test data generated")
        
        # Run all tests
        self.test_cleaner_agent()
        self.test_analyzer_agent()
        self.test_forecasting_agent()
        self.test_prediction_agent()
        self.test_exploration_agent()
        self.test_mcp_classification_models()
        self.test_mcp_recommendation_models()
        self.test_views()
        
        # Print summary
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)
        print(f"✓ Passed: {len(self.results['passed'])}")
        print(f"✗ Failed: {len(self.results['failed'])}")
        print(f"⚠ Warnings: {len(self.results['warnings'])}")
        
        if self.results['passed']:
            print("\nPassed Tests:")
            for test in self.results['passed']:
                print(f"  ✓ {test}")
        
        if self.results['failed']:
            print("\nFailed Tests:")
            for test in self.results['failed']:
                print(f"  ✗ {test}")
        
        print("\n" + "="*60)
        
        return len(self.results['failed']) == 0


if __name__ == "__main__":
    tester = TestAgent()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
