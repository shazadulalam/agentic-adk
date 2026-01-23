"""
Dashboard view components for Dash application
"""
from dash import html, dcc, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path for feature_engineering import
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from feature_engineering import FeatureEngineeringStrategies


class OverviewTabView:
    """View for overview tab with comprehensive data statistics"""
    
    @staticmethod
    def render(df: pd.DataFrame):
        """Render overview tab content with enhanced metrics"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        
        metrics = [
            html.Div([
                html.Div([
                    html.I(className="fas fa-database", style={'fontSize': '32px', 'color': '#667eea', 'marginBottom': '10px'}),
                    html.H4("Dataset Shape", style={'margin': '10px 0'}),
                    html.P(f"{df.shape[0]:,}", style={'fontSize': '36px', 'fontWeight': 'bold', 'color': '#667eea', 'margin': '0'}),
                    html.P("Rows", style={'fontSize': '14px', 'color': '#666', 'margin': '5px 0'}),
                    html.P(f"{df.shape[1]:,} Columns", style={'fontSize': '18px', 'color': '#888', 'margin': '10px 0 0 0'})
                ], style={'textAlign': 'center'})
            ], style={
                'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'color': 'white',
                'padding': '30px',
                'borderRadius': '12px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                'margin': '10px',
                'flex': '1',
                'minWidth': '200px'
            }),
            
            html.Div([
                html.Div([
                    html.I(className="fas fa-memory", style={'fontSize': '32px', 'color': '#28a745', 'marginBottom': '10px'}),
                    html.H4("Memory Usage", style={'margin': '10px 0'}),
                    html.P(f"{df.memory_usage(deep=True).sum() / 1024**2:.2f}", 
                          style={'fontSize': '36px', 'fontWeight': 'bold', 'color': '#28a745', 'margin': '0'}),
                    html.P("MB", style={'fontSize': '14px', 'color': '#666', 'margin': '5px 0'})
                ], style={'textAlign': 'center'})
            ], style={
                'background': 'white',
                'padding': '30px',
                'borderRadius': '12px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                'margin': '10px',
                'flex': '1',
                'minWidth': '200px',
                'border': '2px solid #28a745'
            }),
            
            html.Div([
                html.Div([
                    html.I(className="fas fa-exclamation-triangle", style={'fontSize': '32px', 'color': '#ffc107', 'marginBottom': '10px'}),
                    html.H4("Missing Values", style={'margin': '10px 0'}),
                    html.P(f"{df.isnull().sum().sum():,}", 
                          style={'fontSize': '36px', 'fontWeight': 'bold', 'color': '#ffc107', 'margin': '0'}),
                    html.P(f"({missing_pct:.1f}%)", style={'fontSize': '14px', 'color': '#666', 'margin': '5px 0'})
                ], style={'textAlign': 'center'})
            ], style={
                'background': 'white',
                'padding': '30px',
                'borderRadius': '12px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                'margin': '10px',
                'flex': '1',
                'minWidth': '200px',
                'border': '2px solid #ffc107'
            }),
            
            html.Div([
                html.Div([
                    html.I(className="fas fa-chart-bar", style={'fontSize': '32px', 'color': '#17a2b8', 'marginBottom': '10px'}),
                    html.H4("Numeric Columns", style={'margin': '10px 0'}),
                    html.P(f"{len(numeric_cols)}", 
                          style={'fontSize': '36px', 'fontWeight': 'bold', 'color': '#17a2b8', 'margin': '0'}),
                    html.P(f"{len(categorical_cols)} Categorical", style={'fontSize': '14px', 'color': '#666', 'margin': '5px 0'})
                ], style={'textAlign': 'center'})
            ], style={
                'background': 'white',
                'padding': '30px',
                'borderRadius': '12px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                'margin': '10px',
                'flex': '1',
                'minWidth': '200px',
                'border': '2px solid #17a2b8'
            })
        ]
        
        # Summary statistics for numeric columns
        summary_stats = []
        if len(numeric_cols) > 0:
            summary_df = df[numeric_cols].describe().T.reset_index()
            summary_df.columns = ['Column'] + [col for col in summary_df.columns[1:]]
            summary_stats = summary_df.to_dict('records')
        
        return html.Div([
            html.Div([
                html.H2("📊 Dataset Overview", style={'marginBottom': '20px', 'color': '#333'}),
                html.Div(metrics, style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around', 'marginBottom': '30px'}),
            ]),
            html.Hr(style={'margin': '30px 0'}),
            # Feature Engineering Strategies Section
            OverviewTabView._render_feature_engineering_strategies()
        ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})
    
    @staticmethod
    def _render_feature_engineering_strategies():
        """Render feature engineering strategies in Bootstrap cards"""
        fe = FeatureEngineeringStrategies()
        strategies = fe.get_strategy_summary()
        
        # Color scheme for cards
        colors = ['#667eea', '#48bb78', '#ed8936', '#f56565', '#9f7aea', '#4299e1']
        
        strategy_cards = []
        for idx, strategy in enumerate(strategies):
            color = colors[idx % len(colors)]
            card = html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-cogs", 
                              style={'fontSize': '32px', 'color': color, 'marginBottom': '15px'}),
                        html.H4(strategy['name'], 
                               style={'color': '#333', 'fontWeight': 'bold', 'marginBottom': '10px'}),
                        html.P(strategy['description'], 
                              style={'color': '#666', 'fontSize': '14px', 'marginBottom': '15px', 'lineHeight': '1.6'}),
                        html.Hr(style={'margin': '15px 0', 'borderColor': '#e0e0e0'}),
                        html.Div([
                            html.Strong("Use Cases: ", style={'color': '#333', 'fontSize': '13px'}),
                            html.Span(strategy['use_cases'], 
                                     style={'color': '#666', 'fontSize': '13px'})
                        ], style={'marginBottom': '10px'}),
                        html.Div([
                            html.Strong("Formula: ", style={'color': '#333', 'fontSize': '13px'}),
                            html.Code(strategy['formula'], 
                                     style={'color': color, 'fontSize': '12px', 'backgroundColor': '#f8f9fa', 
                                           'padding': '4px 8px', 'borderRadius': '4px', 'fontFamily': 'monospace'})
                        ])
                    ], style={'padding': '20px'})
                ], className='card', style={
                    'border': 'none',
                    'borderRadius': '12px',
                    'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                    'transition': 'transform 0.2s, box-shadow 0.2s',
                    'height': '100%',
                    'backgroundColor': 'white'
                })
            ], className='col-md-12 col-lg-6', style={'marginBottom': '20px'})
            strategy_cards.append(card)
        
        return html.Div([
            html.Div([
                html.H2("🔧 Feature Engineering Strategies", 
                       style={'color': '#333', 'marginBottom': '10px', 'fontWeight': 'bold'}),
                html.P("Domain-aware feature transformations for enhanced model performance", 
                      style={'color': '#666', 'fontSize': '16px', 'marginBottom': '30px'})
            ], style={'marginBottom': '20px'}),
            html.Div(strategy_cards, className='row', style={'marginBottom': '30px'})
        ], style={'marginTop': '30px'})


class EDATabView:
    """View for EDA tab"""
    
    @staticmethod
    def render(results: dict, df: pd.DataFrame):
        """Render EDA tab content"""
        if not results:
            return html.Div("Click 'Run Full Analysis' to generate EDA results")
        
        content = [html.H2("Exploratory Data Analysis Results")]
        
        if 'data_quality' in results:
            content.append(html.H3("Data Quality"))
            quality = results['data_quality']
            content.append(html.P(f"Duplicate Rows: {quality.get('duplicate_rows', 0)}"))
        
        if 'distributions' in results:
            content.append(html.H3("Distribution Analysis"))
            dist_data = []
            for col, dist_info in results['distributions'].items():
                dist_data.append({
                    'Column': col,
                    'Skewness': f"{dist_info.get('skewness', 0):.3f}",
                    'Kurtosis': f"{dist_info.get('kurtosis', 0):.3f}",
                    'Is Normal': 'Yes' if dist_info.get('is_normal') else 'No'
                })
            content.append(dash_table.DataTable(
                data=dist_data,
                columns=[{'name': col, 'id': col} for col in ['Column', 'Skewness', 'Kurtosis', 'Is Normal']],
                style_cell={'textAlign': 'left', 'padding': '10px'}
            ))
        
        return html.Div(content)


class VisualizationsTabView:
    """View for visualizations tab with interactive graphs"""
    
    @staticmethod
    def render(df: pd.DataFrame, target_col: str = None):
        """Render visualizations tab content with enhanced graphs"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) == 0:
            return html.Div([
                html.Div([
                    html.I(className="fas fa-chart-bar", style={'fontSize': '48px', 'color': '#667eea', 'marginBottom': '20px'}),
                    html.H3("No Numeric Columns Available", style={'color': '#333'}),
                    html.P("Upload a dataset with numeric columns to see visualizations", 
                          style={'color': '#666', 'fontSize': '16px'})
                ], style={'textAlign': 'center', 'padding': '40px'})
            ], style={'backgroundColor': '#f8f9fa', 'borderRadius': '12px', 'margin': '20px'})
        
        content = [html.H2("📊 Interactive Data Visualizations", style={'color': '#333', 'marginBottom': '30px'})]
        
        # Correlation heatmap
        if len(numeric_cols) > 1:
            # Limit to top 20 columns for performance
            cols_to_plot = numeric_cols[:20]
            corr_matrix = df[cols_to_plot].corr()
            fig_corr = px.imshow(corr_matrix, text_auto='.2f', aspect="auto",
                                color_continuous_scale='RdBu', 
                                title="Correlation Matrix (Top 20 Features)")
            fig_corr.update_layout(height=600, template='plotly_white')
            content.append(html.Div([
                html.H3("🔗 Correlation Matrix", style={'marginBottom': '15px', 'color': '#333'}),
                dcc.Graph(figure=fig_corr)
            ], style={'marginBottom': '30px', 'background': 'white', 'padding': '20px', 'borderRadius': '12px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}))
        
        # Distribution plots in a grid
        content.append(html.Div([
            html.H3("📈 Distribution Plots", style={'marginBottom': '15px', 'color': '#333'}),
            html.Div([
                html.Div([
                    dcc.Graph(figure=px.histogram(df, x=col, nbins=30, 
                                                 title=f"Distribution of {col}",
                                                 template='plotly_white').update_layout(height=300))
                ], style={'marginBottom': '20px', 'background': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
                for col in numeric_cols[:9]  # Limit to 9 columns
            ])
        ], style={'marginBottom': '30px'}))
        
        # Box plots
        if len(numeric_cols) > 0:
            content.append(html.Div([
                html.H3("📦 Box Plots (Outlier Detection)", style={'marginBottom': '15px', 'color': '#333'}),
                html.Div([
                    html.Div([
                        dcc.Graph(figure=px.box(df, y=col, title=f"Box Plot: {col}",
                                               template='plotly_white').update_layout(height=300))
                    ], style={'marginBottom': '20px', 'background': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
                    for col in numeric_cols[:9]  # Limit to 9 columns
                ])
            ], style={'marginBottom': '30px'}))
        
        # Scatter plots for top correlated pairs
        if len(numeric_cols) > 1 and len(df) < 10000:  # Only for smaller datasets
            content.append(html.Div([
                html.H3("🔍 Scatter Plots (Top Correlations)", style={'marginBottom': '15px', 'color': '#333'}),
                html.Div([
                    html.Div([
                        dcc.Graph(figure=px.scatter(df, x=col1, y=col2, 
                                                   title=f"{col1} vs {col2}",
                                                   template='plotly_white',
                                                   trendline='ols').update_layout(height=300))
                    ], style={'marginBottom': '20px', 'background': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
                    for col1, col2 in [(numeric_cols[i], numeric_cols[i+1]) for i in range(min(3, len(numeric_cols)-1))]
                ])
            ], style={'marginBottom': '30px'}))
        
        return html.Div(content, style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})


class ForecastingTabView:
    """View for forecasting tab"""
    
    @staticmethod
    def render(results: dict):
        """Render forecasting tab content"""
        if not results:
            return html.Div("Select date and value columns, then click 'Run Full Analysis'")
        
        content = [html.H2("Time Series Forecasting")]
        
        for model_name, model_results in results.items():
            if 'error' in model_results:
                content.append(html.Div(f"{model_name}: {model_results['error']}", 
                                      style={'color': 'red', 'padding': '10px'}))
                continue
            
            content.append(html.H3(f"{model_name.upper()} Forecast"))
            
            if model_name == 'prophet' and 'forecast' in model_results:
                forecast_df = model_results['forecast']
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat'],
                                       mode='lines', name='Forecast', line=dict(color='blue')))
                fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat_upper'],
                                       fill=None, mode='lines', name='Upper Bound', line=dict(width=0)))
                fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat_lower'],
                                       fill='tonexty', mode='lines', name='Lower Bound', line=dict(width=0)))
                fig.update_layout(title=f"{model_name.upper()} Forecast with Confidence Intervals")
                content.append(dcc.Graph(figure=fig))
            elif 'forecast' in model_results:
                forecast = model_results['forecast']
                fig = px.line(y=forecast, title=f"{model_name.upper()} Forecast")
                content.append(dcc.Graph(figure=fig))
        
        return html.Div(content)


class PredictionsTabView:
    """View for predictions tab with model comparison"""
    
    @staticmethod
    def render(results: dict):
        """Render predictions tab content with enhanced comparison"""
        if not results:
            return html.Div([
                html.Div([
                    html.I(className="fas fa-info-circle", style={'fontSize': '48px', 'color': '#667eea', 'marginBottom': '20px'}),
                    html.H3("No Prediction Results Available", style={'color': '#333'}),
                    html.P("Select target column, then click 'Run Full Analysis' to generate predictions", 
                          style={'color': '#666', 'fontSize': '16px'})
                ], style={'textAlign': 'center', 'padding': '40px'})
            ], style={'backgroundColor': '#f8f9fa', 'borderRadius': '12px', 'margin': '20px'})
        
        task_type = results.get('task_type', 'unknown')
        best_model = results.get('best_model', 'N/A')
        
        # Header with task type and best model
        header = html.Div([
            html.Div([
                html.H2("🤖 Predictive Modeling Results", style={'margin': '0', 'color': '#333'}),
                html.Div([
                    html.Span(f"Task Type: ", style={'fontSize': '14px', 'color': '#666'}),
                    html.Span(f"{task_type.upper()}", 
                            style={'fontSize': '18px', 'fontWeight': 'bold', 'color': '#667eea', 'marginLeft': '5px'})
                ], style={'marginTop': '10px'}),
                html.Div([
                    html.Span(f"Best Model: ", style={'fontSize': '14px', 'color': '#666'}),
                    html.Span(f"{best_model.replace('_', ' ').title()}", 
                            style={'fontSize': '18px', 'fontWeight': 'bold', 'color': '#28a745', 'marginLeft': '5px'})
                ], style={'marginTop': '5px'})
            ])
        ], style={
            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'color': 'white',
            'padding': '25px',
            'borderRadius': '12px',
            'marginBottom': '30px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        })
        
        content = [header]
        
        # Model comparison table
        comparison_data = []
        for model_name, model_results in results.items():
            if model_name in ['task_type', 'best_model'] or 'error' in model_results:
                continue
            
            if task_type == 'classification':
                comparison_data.append({
                    'Model': model_name.replace('_', ' ').title(),
                    'Accuracy': f"{model_results.get('accuracy', 0):.4f}",
                    'Precision': f"{model_results.get('precision', 0):.4f}",
                    'Recall': f"{model_results.get('recall', 0):.4f}",
                    'F1 Score': f"{model_results.get('f1', 0):.4f}",
                    'CV Mean': f"{model_results.get('cv_mean', 0):.4f}" if 'cv_mean' in model_results else 'N/A',
                    'Status': '🏆 Best' if model_name == best_model else '✓'
                })
            else:
                comparison_data.append({
                    'Model': model_name.replace('_', ' ').title(),
                    'R² Score': f"{model_results.get('r2', 0):.4f}",
                    'RMSE': f"{model_results.get('rmse', 0):.4f}",
                    'MAE': f"{model_results.get('mae', 0):.4f}",
                    'CV Mean': f"{model_results.get('cv_mean', 0):.4f}" if 'cv_mean' in model_results else 'N/A',
                    'Status': '🏆 Best' if model_name == best_model else '✓'
                })
        
        if comparison_data:
            content.append(html.Div([
                html.H3("📊 Model Comparison", style={'marginBottom': '15px', 'color': '#333'}),
                dash_table.DataTable(
                    data=comparison_data,
                    columns=[{'name': col, 'id': col} for col in comparison_data[0].keys()],
                    style_cell={'textAlign': 'left', 'padding': '12px', 'fontFamily': 'Arial'},
                    style_header={'backgroundColor': '#667eea', 'color': 'white', 'fontWeight': 'bold', 'fontSize': '14px'},
                    style_data={'fontSize': '13px'},
                    style_data_conditional=[
                        {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'},
                        {'if': {'filter_query': '{Status} = 🏆 Best'}, 
                         'backgroundColor': '#d4edda', 'fontWeight': 'bold'}
                    ],
                    sort_action="native",
                    filter_action="native"
                )
            ], style={'marginBottom': '30px'}))
        
        # Individual model details with visualizations
        content.append(html.H3("📈 Model Details & Visualizations", style={'marginBottom': '20px', 'color': '#333'}))
        
        for model_name, model_results in results.items():
            if model_name in ['task_type', 'best_model'] or 'error' in model_results:
                continue
            
            is_best = model_name == best_model
            model_card = html.Div([
                html.Div([
                    html.H4(f"{model_name.replace('_', ' ').title()}", 
                           style={'margin': '0', 'color': '#333'}),
                    html.Span("🏆 Best Model" if is_best else "", 
                            style={'marginLeft': '10px', 'color': '#28a745', 'fontWeight': 'bold'})
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '15px'}),
                
                html.Div([
                    html.Div([
                        html.P("Metrics", style={'fontWeight': 'bold', 'marginBottom': '10px', 'color': '#667eea'}),
                        html.Ul([
                            html.Li(f"{k}: {v:.4f}" if isinstance(v, (int, float)) else f"{k}: {v}")
                            for k, v in model_results.items()
                            if k not in ['model', 'predictions', 'actual', 'confusion_matrix', 'classification_report', 'model_path', 'cv_std']
                        ], style={'listStyle': 'none', 'padding': '0'})
                    ], style={'flex': '1', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px'})
                ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'})
            ], style={
                'background': 'white',
                'padding': '25px',
                'borderRadius': '12px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'marginBottom': '30px',
                'border': '3px solid #28a745' if is_best else '1px solid #ddd'
            })
            
            # Prediction vs Actual plot
            if 'predictions' in model_results and 'actual' in model_results:
                try:
                    preds = model_results['predictions']
                    actual = model_results['actual']
                    
                    # Convert to lists if needed
                    if hasattr(preds, 'values'):
                        preds = preds.values if hasattr(preds, 'values') else list(preds)
                    if hasattr(actual, 'values'):
                        actual = actual.values if hasattr(actual, 'values') else list(actual)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=preds,
                        y=actual,
                        mode='markers',
                        name='Predictions vs Actual',
                        marker=dict(color='#667eea', size=5, opacity=0.6)
                    ))
                    fig.add_trace(go.Scatter(
                        x=actual,
                        y=actual,
                        mode='lines',
                        name='Perfect Prediction',
                        line=dict(dash='dash', color='red', width=2)
                    ))
                    fig.update_layout(
                        title=f"{model_name.replace('_', ' ').title()} - Predictions vs Actual",
                        xaxis_title="Predicted",
                        yaxis_title="Actual",
                        template='plotly_white',
                        height=400
                    )
                    
                    model_card.children.append(html.Div([
                        dcc.Graph(figure=fig)
                    ], style={'marginTop': '20px'}))
                except Exception as e:
                    model_card.children.append(html.P(f"Could not generate plot: {str(e)}", 
                                                       style={'color': 'red', 'fontSize': '12px'}))
            
            content.append(model_card)
        
        return html.Div(content, style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})


class InsightsTabView:
    """View for insights tab"""
    
    @staticmethod
    def render(insights: dict):
        """Render insights tab content"""
        if not insights:
            return html.Div("Click 'Run Full Analysis' to generate insights")
        
        content = [html.H2("Data Insights & Recommendations")]
        
        if 'data_quality' in insights:
            content.append(html.H3("Data Quality Issues"))
            for issue in insights['data_quality']:
                content.append(html.Div([
                    html.I(className="fas fa-exclamation-triangle", style={'color': '#ffc107', 'marginRight': '10px'}),
                    html.Span(issue)
                ], style={'padding': '10px', 'backgroundColor': '#fff3cd', 'margin': '5px 0', 'borderRadius': '5px'}))
        
        if 'patterns' in insights:
            content.append(html.H3("Patterns Detected"))
            for pattern in insights['patterns']:
                content.append(html.Div([
                    html.I(className="fas fa-chart-line", style={'color': '#17a2b8', 'marginRight': '10px'}),
                    html.Span(pattern)
                ], style={'padding': '10px', 'backgroundColor': '#d1ecf1', 'margin': '5px 0', 'borderRadius': '5px'}))
        
        if 'recommendations' in insights:
            content.append(html.H3("Recommendations"))
            for rec in insights['recommendations']:
                content.append(html.Div([
                    html.I(className="fas fa-lightbulb", style={'color': '#28a745', 'marginRight': '10px'}),
                    html.Span(rec)
                ], style={'padding': '10px', 'backgroundColor': '#d4edda', 'margin': '5px 0', 'borderRadius': '5px'}))
        
        return html.Div(content)


class DataTableView:
    """View for data table tab"""
    
    @staticmethod
    def render(df: pd.DataFrame):
        """Render data table tab content"""
        return html.Div([
            html.H2("Data Table"),
            html.P(f"Showing {len(df)} rows"),
            dash_table.DataTable(
                data=df.head(1000).to_dict('records'),
                columns=[{'name': col, 'id': col} for col in df.columns],
                page_size=20,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': '#667eea', 'color': 'white', 'fontWeight': 'bold'},
                filter_action="native",
                sort_action="native"
            )
        ])
