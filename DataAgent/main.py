"""
Main entry point for DataAgent - Comprehensive Data Analysis Platform
"""
import pandas as pd
import os
import argparse
from agents.cleanerAgent import Cleaner
from agents.analyzer import ModelAnalyzer
from agents.forecastingAgent import ForecastingAgent
from agents.predictionAgent import PredictionAgent
from agents.explorationAgent import ExplorationAgent
from config import *

def main():
    """
    Main function to orchestrate all agents for comprehensive data analysis
    """
    parser = argparse.ArgumentParser(description='DataAgent - Comprehensive Data Analysis Platform')
    parser.add_argument('--data', type=str, default='datasets/bq-results-covid-open-data.csv',
                       help='Path to data file (CSV)')
    parser.add_argument('--bigquery', action='store_true',
                       help='Fetch data from BigQuery instead of local file')
    parser.add_argument('--query', type=str, default=None,
                       help='BigQuery SQL query')
    parser.add_argument('--target', type=str, default=None,
                       help='Target column for predictions')
    parser.add_argument('--date-col', type=str, default=None,
                       help='Date column for forecasting')
    parser.add_argument('--value-col', type=str, default=None,
                       help='Value column for forecasting')
    parser.add_argument('--mode', type=str, default='full',
                       choices=['full', 'eda', 'forecast', 'predict', 'explore'],
                       help='Analysis mode')
    parser.add_argument('--dashboard', action='store_true',
                       help='Launch interactive dashboard')
    
    args = parser.parse_args()
    
    # Initialize agents
    cleaner = Cleaner()
    analyzer = ModelAnalyzer()
    forecaster = ForecastingAgent()
    predictor = PredictionAgent()
    explorer = ExplorationAgent()
    
    print("=" * 60)
    print("DataAgent - Comprehensive Data Analysis Platform")
    print("=" * 60)
    
    # Load data
    print("\n[1/6] Loading data...")
    try:
        if args.bigquery and args.query:
            print(f"Fetching data from BigQuery...")
            df = cleaner.fetch_bigquery_data(args.query)
        elif args.bigquery:
            # Default query
            query = f"SELECT * FROM `{BIGQUERY_DATASET}` LIMIT 10000"
            print(f"Using default query: {query}")
            df = cleaner.fetch_bigquery_data(query)
        else:
            print(f"Loading from local file: {args.data}")
            if not os.path.exists(args.data):
                print(f"Warning: File {args.data} not found. Using default dataset.")
                args.data = "datasets/bq-results-covid-open-data.csv"
            df = pd.read_csv(args.data)
        
        print(f"✓ Loaded {len(df)} rows × {len(df.columns)} columns")
    except Exception as e:
        print(f"Error loading data: {e}")
        print("Using default dataset...")
        df = pd.read_csv("datasets/bq-results-covid-open-data.csv")
    
    # Clean data
    print("\n[2/6] Cleaning data...")
    df_cleaned = cleaner.clean_data(df)
    print(f"✓ Data cleaned: {df.shape[0]} → {df_cleaned.shape[0]} rows")
    df = df_cleaned
    
    # Determine target column
    if args.target:
        target_col = args.target
    else:
        # Auto-detect target
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            target_col = numeric_cols[-1]
        else:
            target_col = df.columns[-1]
    
    print(f"Target column: {target_col}")
    
    # Run analysis based on mode
    if args.mode == 'full' or args.mode == 'eda':
        print("\n[3/6] Running Exploratory Data Analysis...")
        try:
            # Use cache to avoid re-processing if dataset hasn't changed
            eda_results = analyzer.analyze_and_plot(df, target_col, use_cache=True)
            print("✓ EDA completed. Reports saved to reports/ directory")
        except Exception as e:
            print(f"Error in EDA: {e}")
    
    if args.mode == 'full' or args.mode == 'explore':
        print("\n[4/6] Generating insights and feature engineering...")
        try:
            # Feature engineering (limit to prevent memory issues)
            df_engineered = explorer.feature_engineering(df)
            print(f"✓ Feature engineering completed: {df.shape[1]} → {df_engineered.shape[1]} features")
            
            # Limit features if too many (for memory safety)
            MAX_FEATURES = 500
            if df_engineered.shape[1] > MAX_FEATURES:
                print(f"⚠ Limiting to top {MAX_FEATURES} features (out of {df_engineered.shape[1]}) for memory safety")
                numeric_cols = df_engineered.select_dtypes(include=['number']).columns
                if len(numeric_cols) > MAX_FEATURES:
                    # Select features with highest variance
                    feature_variance = df_engineered[numeric_cols].var().sort_values(ascending=False)
                    top_features = feature_variance.head(MAX_FEATURES).index.tolist()
                    if target_col in df_engineered.columns:
                        top_features.append(target_col)
                    df_engineered = df_engineered[top_features]
            
            # Generate insights
            insights = explorer.generate_insights(df, target_col)
            print("\n📊 Key Insights:")
            for category, items in insights.items():
                if items:
                    print(f"\n{category.replace('_', ' ').title()}:")
                    for item in items[:3]:  # Show top 3
                        print(f"  • {item}")
        except Exception as e:
            print(f"Error in exploration: {e}")
            import traceback
            traceback.print_exc()
    
    if args.mode == 'full' or args.mode == 'forecast':
        if args.date_col and args.value_col:
            print("\n[5/6] Running Time Series Forecasting...")
            try:
                ts = forecaster.prepare_time_series(df, args.date_col, args.value_col)
                forecast_results = forecaster.compare_forecasts(ts, FORECAST_HORIZON)
                print("✓ Forecasting completed")
                for model_name, result in forecast_results.items():
                    if 'error' not in result:
                        print(f"  • {model_name}: Success")
                    else:
                        print(f"  • {model_name}: {result['error']}")
            except Exception as e:
                print(f"Error in forecasting: {e}")
        else:
            print("\n[5/6] Skipping forecasting (date and value columns not specified)")
    
    if args.mode == 'full' or args.mode == 'predict':
        print("\n" + "="*60)
        print("[6/6] Training Predictive Models...")
        print("="*60)
        try:
            # Use engineered features if available, otherwise use original
            if args.mode == 'full' and 'df_engineered' in locals():
                print("  Using feature-engineered dataset")
                training_df = df_engineered
            else:
                training_df = df
            
            print(f"\n📊 Dataset Info:")
            print(f"  • Rows: {len(training_df):,}")
            print(f"  • Features: {len(training_df.columns):,}")
            print(f"  • Target: {target_col}")
            import sys
            sys.stdout.flush()
            
            print(f"\n🔄 Starting model training...")
            sys.stdout.flush()
            prediction_results = predictor.auto_train(training_df, target_col)
            sys.stdout.flush()
            
            task_type = prediction_results.get('task_type', 'unknown')
            best_model = prediction_results.get('best_model', 'N/A')
            
            print("\n" + "="*60)
            print("📈 MODEL TRAINING RESULTS")
            print("="*60)
            print(f"\nTask Type: {task_type.upper()}")
            print(f"Models Trained: {len([k for k in prediction_results.keys() if k not in ['task_type', 'best_model']])}")
            
            # Display results for all models
            print("\n" + "-"*60)
            print("MODEL PERFORMANCE METRICS")
            print("-"*60)
            
            if task_type == 'classification':
                # Classification metrics table
                print(f"\n{'Model':<25} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'CV Score':<12}")
                print("-"*85)
                
                for model_name in sorted([k for k in prediction_results.keys() if k not in ['task_type', 'best_model']]):
                    if 'error' in prediction_results[model_name]:
                        print(f"{model_name:<25} {'ERROR':<12} {'-':<12} {'-':<12} {'-':<12} {'-':<12}")
                        print(f"  └─ {prediction_results[model_name]['error']}")
                    else:
                        result = prediction_results[model_name]
                        acc = result.get('accuracy', 0)
                        prec = result.get('precision', 0)
                        rec = result.get('recall', 0)
                        f1 = result.get('f1', 0)
                        cv_mean = result.get('cv_mean', 0)
                        cv_std = result.get('cv_std', 0)
                        
                        marker = "⭐" if model_name == best_model else "  "
                        print(f"{marker} {model_name:<23} {acc:<12.4f} {prec:<12.4f} {rec:<12.4f} {f1:<12.4f} {cv_mean:.4f}±{cv_std:.4f}")
                        
                        # Show confusion matrix for best model
                        if model_name == best_model and 'confusion_matrix' in result:
                            print(f"\n  📊 Confusion Matrix ({model_name}):")
                            cm = result['confusion_matrix']
                            print(f"  {cm}")
                            
            else:
                # Regression metrics table
                print(f"\n{'Model':<25} {'R² Score':<12} {'RMSE':<12} {'MAE':<12} {'MSE':<12} {'CV Score':<12}")
                print("-"*85)
                
                for model_name in sorted([k for k in prediction_results.keys() if k not in ['task_type', 'best_model']]):
                    if 'error' in prediction_results[model_name]:
                        print(f"{model_name:<25} {'ERROR':<12} {'-':<12} {'-':<12} {'-':<12} {'-':<12}")
                        print(f"  └─ {prediction_results[model_name]['error']}")
                    else:
                        result = prediction_results[model_name]
                        r2 = result.get('r2', 0)
                        rmse = result.get('rmse', 0)
                        mae = result.get('mae', 0)
                        mse = result.get('mse', 0)
                        cv_mean = result.get('cv_mean', 0)
                        cv_std = result.get('cv_std', 0)
                        
                        marker = "⭐" if model_name == best_model else "  "
                        print(f"{marker} {model_name:<23} {r2:<12.4f} {rmse:<12.2f} {mae:<12.2f} {mse:<12.2f} {cv_mean:.4f}±{cv_std:.4f}")
            
            # Best model summary
            print("\n" + "="*60)
            print("🏆 BEST MODEL SUMMARY")
            print("="*60)
            print(f"\nBest Model: {best_model}")
            
            if best_model in prediction_results and 'error' not in prediction_results[best_model]:
                best_result = prediction_results[best_model]
                
                if task_type == 'classification':
                    print(f"\n📊 Performance Metrics:")
                    print(f"  • Accuracy:  {best_result.get('accuracy', 0):.4f} ({best_result.get('accuracy', 0)*100:.2f}%)")
                    print(f"  • Precision: {best_result.get('precision', 0):.4f}")
                    print(f"  • Recall:    {best_result.get('recall', 0):.4f}")
                    print(f"  • F1-Score:  {best_result.get('f1', 0):.4f}")
                    print(f"  • CV Score:  {best_result.get('cv_mean', 0):.4f} ± {best_result.get('cv_std', 0):.4f}")
                    
                    if 'classification_report' in best_result:
                        print(f"\n📋 Detailed Classification Report:")
                        print(best_result['classification_report'])
                        
                else:
                    print(f"\n📊 Performance Metrics:")
                    print(f"  • R² Score:  {best_result.get('r2', 0):.4f} ({best_result.get('r2', 0)*100:.2f}% variance explained)")
                    print(f"  • RMSE:      {best_result.get('rmse', 0):.4f}")
                    print(f"  • MAE:       {best_result.get('mae', 0):.4f}")
                    print(f"  • MSE:       {best_result.get('mse', 0):.4f}")
                    print(f"  • CV Score:  {best_result.get('cv_mean', 0):.4f} ± {best_result.get('cv_std', 0):.4f}")
                
                if 'model_path' in best_result:
                    print(f"\n  Model saved to: {best_result['model_path']}")
            
            print("\n" + "="*60)
            print("✓ Model training completed successfully!")
            print("="*60)
            import sys
            sys.stdout.flush()
            
        except Exception as e:
            print(f"\n Error in prediction: {e}")
            import traceback
            traceback.print_exc()
            import sys
            sys.stdout.flush()
    
    print("\n" + "=" * 60)
    print("Analysis Complete!")
    print("=" * 60)
    print(f"\nReports saved to: {REPORTS_DIR}/")
    print(f"Models saved to: {MODELS_DIR}/")
    import sys
    sys.stdout.flush()
    
    # Launch dashboard automatically after training (unless explicitly disabled)
    # User can interrupt with Ctrl+C if they don't want the dashboard
    try:
        print("\n" + "="*60)
        print("🚀 Launching Interactive Dashboard...")
        print("="*60)
        print("\n📊 Dashboard will be available at:")
        print("   → http://localhost:8050")
        print("   → http://127.0.0.1:8050")
        print("\n💡 Tips:")
        print("   - Upload a CSV file or use the default dataset")
        print("   - Select target column for predictions")
        print("   - Click 'Run Full Analysis' to generate results")
        print("\n⏹️  Press Ctrl+C to stop the server")
        print("="*60 + "\n")
        sys.stdout.flush()
        
        # Import and create dashboard app with the current data
        from dashboards.dashboard import app
        app.run_server(debug=False, host='0.0.0.0', port=8050, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n⚠️  Dashboard launch interrupted by user")
        print("Analysis results are still available in reports/ and models/ directories")
        sys.exit(0)
    except Exception as e:
        print(f"\n⚠️  Could not launch dashboard: {e}")
        print("Analysis results are still available in reports/ and models/ directories")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

