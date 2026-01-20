"""
Dashboard view components for Dash application
"""
from dash import html, dcc, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


class OverviewTabView:
    """View for overview tab"""
    
    @staticmethod
    def render(df: pd.DataFrame):
        """Render overview tab content"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        metrics = [
            html.Div([
                html.H4("Dataset Shape", style={'margin': '0'}),
                html.P(f"{df.shape[0]:,} rows", style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#667eea'}),
                html.P(f"{df.shape[1]:,} columns", style={'fontSize': '18px', 'color': '#666'})
            ], className='metric-card'),
            
            html.Div([
                html.H4("Memory Usage", style={'margin': '0'}),
                html.P(f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB", 
                      style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#667eea'})
            ], className='metric-card'),
            
            html.Div([
                html.H4("Missing Values", style={'margin': '0'}),
                html.P(f"{df.isnull().sum().sum():,}", 
                      style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#667eea'})
            ], className='metric-card'),
            
            html.Div([
                html.H4("Numeric Columns", style={'margin': '0'}),
                html.P(f"{len(numeric_cols)}", 
                      style={'fontSize': '24px', 'fontWeight': 'bold', 'color': '#667eea'})
            ], className='metric-card')
        ]
        
        return html.Div([
            html.Div(metrics, style={'display': 'flex', 'flexWrap': 'wrap'}),
            html.Hr(),
            html.H3("Column Information"),
            dash_table.DataTable(
                data=df.dtypes.reset_index().to_dict('records'),
                columns=[{'name': 'Column', 'id': 'index'}, {'name': 'Data Type', 'id': 0}],
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': '#667eea', 'color': 'white', 'fontWeight': 'bold'}
            )
        ])


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
    """View for visualizations tab"""
    
    @staticmethod
    def render(df: pd.DataFrame, target_col: str = None):
        """Render visualizations tab content"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) == 0:
            return html.Div("No numeric columns available for visualization")
        
        # Correlation heatmap
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                                color_continuous_scale='RdBu', title="Correlation Matrix")
        else:
            fig_corr = None
        
        # Distribution plots
        figs = []
        for col in numeric_cols[:6]:  # Limit to 6 columns
            fig = px.histogram(df, x=col, nbins=30, title=f"Distribution of {col}")
            figs.append(dcc.Graph(figure=fig))
        
        content = [html.H2("Data Visualizations")]
        
        if fig_corr:
            content.append(html.H3("Correlation Matrix"))
            content.append(dcc.Graph(figure=fig_corr))
        
        content.append(html.H3("Distributions"))
        content.extend(figs)
        
        # Box plots
        if len(numeric_cols) > 0:
            content.append(html.H3("Box Plots"))
            for col in numeric_cols[:6]:
                fig = px.box(df, y=col, title=f"Box Plot: {col}")
                content.append(dcc.Graph(figure=fig))
        
        return html.Div(content)


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
    """View for predictions tab"""
    
    @staticmethod
    def render(results: dict):
        """Render predictions tab content"""
        if not results:
            return html.Div("Select target column, then click 'Run Full Analysis'")
        
        content = [html.H2("Predictive Modeling Results")]
        content.append(html.H3(f"Task Type: {results.get('task_type', 'Unknown').upper()}"))
        content.append(html.H3(f"Best Model: {results.get('best_model', 'N/A')}"))
        
        task_type = results.get('task_type')
        
        for model_name, model_results in results.items():
            if model_name in ['task_type', 'best_model'] or 'error' in model_results:
                continue
            
            content.append(html.H4(f"{model_name.replace('_', ' ').title()}"))
            
            if task_type == 'classification':
                metrics = [
                    f"Accuracy: {model_results.get('accuracy', 0):.4f}",
                    f"Precision: {model_results.get('precision', 0):.4f}",
                    f"Recall: {model_results.get('recall', 0):.4f}",
                    f"F1 Score: {model_results.get('f1', 0):.4f}"
                ]
            else:
                metrics = [
                    f"R² Score: {model_results.get('r2', 0):.4f}",
                    f"RMSE: {model_results.get('rmse', 0):.4f}",
                    f"MAE: {model_results.get('mae', 0):.4f}"
                ]
            
            content.append(html.Ul([html.Li(m) for m in metrics]))
            
            # Prediction vs Actual plot
            if 'predictions' in model_results and 'actual' in model_results:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=model_results['actual'],
                    x=model_results['predictions'],
                    mode='markers',
                    name='Predictions vs Actual'
                ))
                fig.add_trace(go.Scatter(
                    y=model_results['actual'],
                    x=model_results['actual'],
                    mode='lines',
                    name='Perfect Prediction',
                    line=dict(dash='dash', color='red')
                ))
                fig.update_layout(
                    title=f"{model_name} - Predictions vs Actual",
                    xaxis_title="Predicted",
                    yaxis_title="Actual"
                )
                content.append(dcc.Graph(figure=fig))
        
        return html.Div(content)


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
