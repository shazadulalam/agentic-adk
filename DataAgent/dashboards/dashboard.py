import dash
from dash import html, dcc, Input, Output, State, dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import os
import json
import base64
import io
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import agents
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.cleanerAgent import Cleaner
from agents.analyzer import ModelAnalyzer
from agents.forecastingAgent import ForecastingAgent
from agents.predictionAgent import PredictionAgent
from agents.explorationAgent import ExplorationAgent
from config import *

# Initialize agents
cleaner = Cleaner()
analyzer = ModelAnalyzer()
forecaster = ForecastingAgent()
predictor = PredictionAgent()
explorer = ExplorationAgent()

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
])

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>DataAgent - Comprehensive Data Analysis Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .metric-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin: 10px;
            }
            .tab-content {
                padding: 20px;
            }
            .upload-area {
                border: 2px dashed #667eea;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                background: #f8f9fa;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Global variable to store current data
current_df = None
analysis_results = {}

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("📊 DataAgent - Comprehensive Data Analysis Platform", 
                style={'textAlign': 'center', 'margin': '0'}),
        html.P("Advanced Analytics, Forecasting, and Predictive Modeling", 
               style={'textAlign': 'center', 'margin': '10px 0 0 0', 'opacity': 0.9})
    ], className='header'),
    
    # Main content
    html.Div([
        # Sidebar
        html.Div([
            html.H3("📁 Data Source", style={'marginTop': '20px'}),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    html.I(className="fas fa-cloud-upload-alt", style={'fontSize': '48px', 'color': '#667eea'}),
                    html.P('Drag and Drop or Click to Upload CSV', style={'marginTop': '10px'})
                ]),
                style={
                    'width': '100%',
                    'height': '150px',
                    'lineHeight': '150px',
                    'borderWidth': '2px',
                    'borderStyle': 'dashed',
                    'borderRadius': '10px',
                    'textAlign': 'center',
                    'margin': '20px 0',
                    'cursor': 'pointer'
                },
                multiple=False
            ),
            
            html.Hr(),
            
            html.H3("⚙️ Configuration"),
            html.Label("Target Column (for predictions):"),
            dcc.Dropdown(
                id='target-column',
                options=[],
                placeholder="Select target column",
                style={'marginBottom': '20px'}
            ),
            
            html.Label("Date Column (for forecasting):"),
            dcc.Dropdown(
                id='date-column',
                options=[],
                placeholder="Select date column",
                style={'marginBottom': '20px'}
            ),
            
            html.Label("Value Column (for forecasting):"),
            dcc.Dropdown(
                id='value-column',
                options=[],
                placeholder="Select value column",
                style={'marginBottom': '20px'}
            ),
            
            html.Button("🔄 Run Full Analysis", id='run-analysis', n_clicks=0,
                       style={
                           'width': '100%',
                           'padding': '15px',
                           'backgroundColor': '#667eea',
                           'color': 'white',
                           'border': 'none',
                           'borderRadius': '5px',
                           'fontSize': '16px',
                           'cursor': 'pointer',
                           'marginTop': '20px'
                       }),
            
            html.Div(id='status-message', style={'marginTop': '20px', 'padding': '10px'})
            
        ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top', 
                  'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px',
                  'marginRight': '20px'}),
        
        # Main content area
        html.Div([
            dcc.Tabs(id='main-tabs', value='overview', children=[
                dcc.Tab(label='📈 Overview', value='overview'),
                dcc.Tab(label='🔍 Exploratory Analysis', value='eda'),
                dcc.Tab(label='📊 Visualizations', value='visualizations'),
                dcc.Tab(label='🔮 Forecasting', value='forecasting'),
                dcc.Tab(label='🤖 Predictions', value='predictions'),
                dcc.Tab(label='💡 Insights', value='insights'),
                dcc.Tab(label='📋 Data Table', value='data-table')
            ]),
            
            html.Div(id='tab-content', className='tab-content')
        ], style={'width': '70%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'display': 'flex', 'padding': '20px'})
])

# Callbacks
@app.callback(
    [Output('target-column', 'options'),
     Output('date-column', 'options'),
     Output('value-column', 'options'),
     Output('status-message', 'children')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_columns(contents, filename):
    global current_df
    
    if contents is None:
        return [], [], [], ""
    
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        if filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        else:
            return [], [], [], html.Div("Please upload a CSV file", style={'color': 'red'})
        
        current_df = df
        
        options = [{'label': col, 'value': col} for col in df.columns]
        
        # Try to identify date columns
        date_options = []
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]' or 'date' in col.lower() or 'time' in col.lower():
                date_options.append({'label': col, 'value': col})
        
        # Try to identify numeric columns for value column
        numeric_options = [{'label': col, 'value': col} for col in df.select_dtypes(include=[np.number]).columns]
        
        return options, date_options, numeric_options, html.Div(
            f"✅ Loaded {len(df)} rows × {len(df.columns)} columns", 
            style={'color': 'green', 'fontWeight': 'bold'}
        )
    except Exception as e:
        return [], [], [], html.Div(f"Error: {str(e)}", style={'color': 'red'})


@app.callback(
    Output('tab-content', 'children'),
    [Input('main-tabs', 'value'),
     Input('run-analysis', 'n_clicks')],
    [State('target-column', 'value'),
     State('date-column', 'value'),
     State('value-column', 'value')]
)
def update_tab_content(tab, n_clicks, target_col, date_col, value_col):
    global current_df, analysis_results
    
    if current_df is None or len(current_df) == 0:
        return html.Div([
            html.H3("No data loaded"),
            html.P("Please upload a CSV file to begin analysis")
        ])
    
    # Import views
    from views.dashboard_views import (
        OverviewTabView, EDATabView, VisualizationsTabView,
        ForecastingTabView, PredictionsTabView, InsightsTabView, DataTableView
    )
    
    if tab == 'overview':
        return OverviewTabView.render(current_df)
    
    elif tab == 'eda':
        if n_clicks > 0:
            try:
                results = analyzer.analyze_and_plot(current_df, target_col)
                analysis_results['eda'] = results
            except Exception as e:
                return html.Div(f"Error in EDA: {str(e)}", style={'color': 'red'})
        return EDATabView.render(analysis_results.get('eda', {}), current_df)
    
    elif tab == 'visualizations':
        return VisualizationsTabView.render(current_df, target_col)
    
    elif tab == 'forecasting':
        if n_clicks > 0 and date_col and value_col:
            try:
                results = run_forecasting(current_df, date_col, value_col)
                analysis_results['forecasting'] = results
            except Exception as e:
                return html.Div(f"Error in forecasting: {str(e)}", style={'color': 'red'})
        return ForecastingTabView.render(analysis_results.get('forecasting', {}))
    
    elif tab == 'predictions':
        if n_clicks > 0 and target_col:
            try:
                results = predictor.auto_train(current_df, target_col)
                analysis_results['predictions'] = results
            except Exception as e:
                return html.Div(f"Error in predictions: {str(e)}", style={'color': 'red'})
        return PredictionsTabView.render(analysis_results.get('predictions', {}))
    
    elif tab == 'insights':
        if n_clicks > 0:
            try:
                insights = explorer.generate_insights(current_df, target_col)
                analysis_results['insights'] = insights
            except Exception as e:
                return html.Div(f"Error generating insights: {str(e)}", style={'color': 'red'})
        return InsightsTabView.render(analysis_results.get('insights', {}))
    
    elif tab == 'data-table':
        return DataTableView.render(current_df)
    
    return html.Div("Select a tab")


def run_forecasting(df, date_col, value_col):
    """Run forecasting analysis"""
    ts = forecaster.prepare_time_series(df, date_col, value_col)
    results = forecaster.compare_forecasts(ts, FORECAST_HORIZON)
    return results


if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=8050)

