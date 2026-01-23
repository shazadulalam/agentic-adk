"""
Enhanced DataAgent Dashboard with File Upload, Date Filtering, and Modern UI
Inspired by Django template but built with Dash/Plotly
"""
import dash
from dash import html, dcc, Input, Output, State, dash_table, callback_context
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

# Import agents and utilities
import sys
# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from agents.cleanerAgent import Cleaner
from agents.analyzer import ModelAnalyzer
from agents.forecastingAgent import ForecastingAgent
from agents.predictionAgent import PredictionAgent
from agents.explorationAgent import ExplorationAgent
from utils.data_loader import UniversalDataLoader
from config import *

# Initialize agents
cleaner = Cleaner()
analyzer = ModelAnalyzer()
forecaster = ForecastingAgent()
predictor = PredictionAgent()
explorer = ExplorationAgent()
data_loader = UniversalDataLoader()

# Initialize Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
])

# Add custom CSS for sidebar navigation
app.index_string = app.index_string.replace(
    '</head>',
    '''
    <style>
        .list-group-item {
            transition: all 0.3s ease;
        }
        .list-group-item:hover {
            background-color: #f8f9fa !important;
            transform: translateX(5px);
        }
        .list-group-item.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border-left: 4px solid #764ba2 !important;
        }
        .list-group-item.active i {
            color: white !important;
        }
    </style>
    </head>
    ''' if '</head>' in app.index_string else ''
)

# Load HTML template from views folder
from views.template_renderer import get_renderer

renderer = get_renderer()
base_template = renderer.load_template('dashboard_base.html')
# Add custom CSS for sidebar navigation
app.index_string = base_template.replace(
    '</head>',
    '''
    <style>
        .list-group-item {
            transition: all 0.3s ease;
            border: none !important;
        }
        .list-group-item:hover {
            background-color: #f8f9fa !important;
            transform: translateX(5px);
        }
        .list-group-item.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border-left: 4px solid #764ba2 !important;
        }
        .list-group-item.active i {
            color: white !important;
        }
    </style>
    </head>
    '''
)

# Global variables
current_df = None
filtered_df = None
analysis_results = {}
date_column_detected = None

# Try to load default dataset
try:
    default_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                     'datasets', 'bq-results-covid-open-data.csv')
    if os.path.exists(default_data_path):
        current_df = data_loader.load(default_data_path)
        if len(current_df) > 10000:
            current_df = current_df.head(10000)  # Limit for dashboard performance
        filtered_df = current_df.copy()
        print(f"✓ Loaded default dataset: {len(current_df):,} rows")
except Exception as e:
    print(f"Could not load default dataset: {e}")

def detect_date_column(df):
    """Detect date column in dataframe"""
    if df is None or len(df) == 0:
        return None
    
    # Check for explicit datetime columns
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    
    # Check for columns with 'date' or 'time' in name
    for col in df.columns:
        col_lower = col.lower()
        if 'date' in col_lower or 'time' in col_lower or 'timestamp' in col_lower:
            try:
                pd.to_datetime(df[col].dropna().iloc[0:10])
                return col
            except:
                continue
    
    return None

# Import HTML component generator
from views.html_components import get_html_generator

html_gen = get_html_generator()

# Import views at module level (optimization)
from views.dashboard_views import (
    OverviewTabView, EDATabView, VisualizationsTabView,
    ForecastingTabView, PredictionsTabView, InsightsTabView, DataTableView
)

def create_metric_card(icon, value, label, color="#667eea"):
    """Create a metric card component using HTML template"""
    return html_gen.metric_card(icon, str(value), label, color)

# App Layout
app.layout = html.Div([
    dcc.Store(id='data-store'),
    dcc.Store(id='filtered-data-store'),
    
    # Header
    html.Div([
        html.Div([
            html.H1("📊 DataAgent Analytics Dashboard", 
                   style={'margin': '0', 'fontWeight': '700', 'fontSize': '32px'}),
            html.P("Advanced Data Analysis, Forecasting & Predictive Modeling", 
                   style={'margin': '10px 0 0 0', 'opacity': 0.9, 'fontSize': '16px'})
        ], className='container-fluid')
    ], className='header-gradient'),
    
    # Main Content
    html.Div([
        html.Div([
            # Sidebar
            html.Div([
                # Navigation Tabs (Sidebar)
                html.Div([
                    html.Div([
                        html.A([
                            html.I(className="fas fa-home", style={'marginRight': '10px'}),
                            "Home"
                        ], href="#", className="list-group-item list-group-item-action", id="nav-overview", n_clicks=0,
                        style={'cursor': 'pointer', 'border': 'none', 'padding': '12px 15px', 'borderRadius': '5px', 'marginBottom': '5px'}),
                        html.A([
                            html.I(className="fas fa-chart-bar", style={'marginRight': '10px'}),
                            "Visualizations"
                        ], href="#", className="list-group-item list-group-item-action", id="nav-visualizations", n_clicks=0,
                        style={'cursor': 'pointer', 'border': 'none', 'padding': '12px 15px', 'borderRadius': '5px', 'marginBottom': '5px'}),
                        html.A([
                            html.I(className="fas fa-search", style={'marginRight': '10px'}),
                            "EDA Analysis"
                        ], href="#", className="list-group-item list-group-item-action", id="nav-eda", n_clicks=0,
                        style={'cursor': 'pointer', 'border': 'none', 'padding': '12px 15px', 'borderRadius': '5px', 'marginBottom': '5px'}),
                        html.A([
                            html.I(className="fas fa-chart-line", style={'marginRight': '10px'}),
                            "Forecasting"
                        ], href="#", className="list-group-item list-group-item-action", id="nav-forecasting", n_clicks=0,
                        style={'cursor': 'pointer', 'border': 'none', 'padding': '12px 15px', 'borderRadius': '5px', 'marginBottom': '5px'}),
                        html.A([
                            html.I(className="fas fa-robot", style={'marginRight': '10px'}),
                            "Predictions"
                        ], href="#", className="list-group-item list-group-item-action", id="nav-predictions", n_clicks=0,
                        style={'cursor': 'pointer', 'border': 'none', 'padding': '12px 15px', 'borderRadius': '5px', 'marginBottom': '5px'}),
                        html.A([
                            html.I(className="fas fa-lightbulb", style={'marginRight': '10px'}),
                            "Insights"
                        ], href="#", className="list-group-item list-group-item-action", id="nav-insights", n_clicks=0,
                        style={'cursor': 'pointer', 'border': 'none', 'padding': '12px 15px', 'borderRadius': '5px', 'marginBottom': '5px'}),
                        html.A([
                            html.I(className="fas fa-table", style={'marginRight': '10px'}),
                            "Data Table"
                        ], href="#", className="list-group-item list-group-item-action", id="nav-data-table", n_clicks=0,
                        style={'cursor': 'pointer', 'border': 'none', 'padding': '12px 15px', 'borderRadius': '5px'})
                    ], className="list-group", style={'border': 'none'})
                ], style={'marginBottom': '30px'}),
                
                html.Hr(style={'margin': '25px 0'}),
                
                html.H4("📁 Data Source", style={'marginBottom': '20px', 'fontWeight': '600'}),
                
                # File Upload (using HTML template)
                dcc.Upload(
                    id='upload-data',
                    children=html_gen.upload_area(),
                    style={'width': '100%'},
                    multiple=False
                ),
                
                html.Div(id='upload-status', style={'marginTop': '15px'}),
                
                html.Hr(style={'margin': '25px 0'}),
                
                # Date Range Filter (using HTML template)
                html.Div(id='date-filter-section', children=html_gen.date_filter_section()),
                
                html.Hr(style={'margin': '25px 0'}),
                
                # Configuration
                html.H5("⚙️ Configuration", style={'marginBottom': '15px', 'fontWeight': '600'}),
                html.Label("Target Column:", style={'fontSize': '12px', 'fontWeight': '500', 'color': '#4a5568'}),
                dcc.Dropdown(
                    id='target-column',
                    options=[],
                    placeholder="Select target column",
                    style={'marginBottom': '20px'}
                ),
                html.Label("Date Column:", style={'fontSize': '12px', 'fontWeight': '500', 'color': '#4a5568'}),
                dcc.Dropdown(
                    id='date-column',
                    options=[],
                    placeholder="Select date column",
                    style={'marginBottom': '20px'}
                ),
                html.Label("Value Column:", style={'fontSize': '12px', 'fontWeight': '500', 'color': '#4a5568'}),
                dcc.Dropdown(
                    id='value-column',
                    options=[],
                    placeholder="Select value column",
                    style={'marginBottom': '20px'}
                ),
                
                html.Button("🔄 Run Full Analysis", id='run-analysis', n_clicks=0,
                           className='btn btn-primary btn-primary-custom',
                           style={'width': '100%', 'marginTop': '20px', 'padding': '15px'})
                
            ], className='sidebar col-md-3'),
            
            # Main Content Area
            html.Div([
                # Metrics Cards Row (Above tabs)
                html.Div(id='metrics-row', className='row', style={'marginBottom': '30px'}),
                
                # Date Range Display
                html.Div(id='date-range-display', style={'marginBottom': '20px'}),
                
                # Hidden Tabs (for state management)
                dcc.Tabs(id='main-tabs', value='overview', children=[
                    dcc.Tab(label='Overview', value='overview'),
                    dcc.Tab(label='Visualizations', value='visualizations'),
                    dcc.Tab(label='EDA Analysis', value='eda'),
                    dcc.Tab(label='Forecasting', value='forecasting'),
                    dcc.Tab(label='Predictions', value='predictions'),
                    dcc.Tab(label='Insights', value='insights'),
                    dcc.Tab(label='Data Table', value='data-table')
                ], style={'display': 'none'}),
                
                # Tab Content
                html.Div(id='tab-content', className='tab-content-wrapper')
                
            ], className='col-md-9')
        ], className='row', style={'padding': '20px'})
    ], className='container-fluid')
])

# Callback: Handle file upload
@app.callback(
    [Output('data-store', 'data'),
     Output('target-column', 'options'),
     Output('date-column', 'options'),
     Output('value-column', 'options'),
     Output('upload-status', 'children'),
     Output('date-filter-section', 'style')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def handle_upload(contents, filename):
    global current_df, filtered_df
    
    if contents is None:
        # Return default dataset options
        if current_df is not None:
            options = [{'label': col, 'value': col} for col in current_df.columns]
            date_options = []
            for col in current_df.columns:
                if pd.api.types.is_datetime64_any_dtype(current_df[col]) or 'date' in col.lower():
                    date_options.append({'label': col, 'value': col})
            numeric_options = [{'label': col, 'value': col} 
                             for col in current_df.select_dtypes(include=[np.number]).columns]
            
            date_col = detect_date_column(current_df)
            show_date_filter = {'display': 'block'} if date_col else {'display': 'none'}
            
            status_msg = html.Div([
                html_gen.status_badge("✅ Default dataset loaded", 'success'),
                html.P(f"{len(current_df):,} rows × {len(current_df.columns)} columns", 
                      style={'margin': '5px 0 0 0', 'fontSize': '12px', 'color': '#718096'})
            ])
            return (
                current_df.to_dict('records'),
                options,
                date_options,
                numeric_options,
                status_msg,
                show_date_filter
            )
        return None, [], [], [], html_gen.status_badge("No data loaded", 'error'), {'display': 'none'}
    
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Use universal data loader
        if filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif filename.endswith(('.xlsx', '.xls', '.xlsm', '.xlsb')):
            # For Excel, we need to save temporarily or use openpyxl
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                tmp.write(decoded)
                tmp_path = tmp.name
            df = data_loader.load(tmp_path)
            os.unlink(tmp_path)
        else:
            return None, [], [], [], html.Div("Unsupported file format", 
                                            className='status-badge status-error'), {'display': 'none'}
        
        # Limit size for dashboard performance
        if len(df) > 10000:
            df = df.head(10000)
        
        current_df = df
        filtered_df = df.copy()
        
        options = [{'label': col, 'value': col} for col in df.columns]
        date_options = []
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]) or 'date' in col.lower() or 'time' in col.lower():
                date_options.append({'label': col, 'value': col})
        numeric_options = [{'label': col, 'value': col} 
                         for col in df.select_dtypes(include=[np.number]).columns]
        
        date_col = detect_date_column(df)
        show_date_filter = {'display': 'block'} if date_col else {'display': 'none'}
        
        status_msg = html.Div([
            html_gen.status_badge(f"✅ {filename} loaded", 'success'),
            html.P(f"{len(df):,} rows × {len(df.columns)} columns", 
                  style={'margin': '5px 0 0 0', 'fontSize': '12px', 'color': '#718096'})
        ])
        return (
            df.to_dict('records'),
            options,
            date_options,
            numeric_options,
            status_msg,
            show_date_filter
        )
    except Exception as e:
        return None, [], [], [], html_gen.status_badge(f"Error: {str(e)}", 'error'), {'display': 'none'}

# Callback: Date filtering
@app.callback(
    [Output('filtered-data-store', 'data'),
     Output('date-range-display', 'children')],
    [Input('apply-date-filter', 'n_clicks'),
     Input('clear-date-filter', 'n_clicks')],
    [State('start-date', 'date'),
     State('end-date', 'date'),
     State('date-column', 'value'),
     State('data-store', 'data')]
)
def filter_by_date(apply_clicks, clear_clicks, start_date, end_date, date_col, data):
    global filtered_df
    
    ctx = callback_context
    if not ctx.triggered:
        if current_df is not None:
            filtered_df = current_df.copy()
            return current_df.to_dict('records'), ""
        return data, ""
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'clear-date-filter':
        if current_df is not None:
            filtered_df = current_df.copy()
            return current_df.to_dict('records'), ""
        return data, ""
    
    if trigger_id == 'apply-date-filter' and date_col and start_date and end_date and data:
        df = pd.DataFrame(data)
        
        # Convert date column to datetime
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            
            # Filter
            mask = (df[date_col] >= start) & (df[date_col] <= end)
            filtered_df = df[mask].copy()
            
            return (
                filtered_df.to_dict('records'),
                html.Div([
                    html.P([
                        html.Strong("Showing data: "),
                        html.Span(f"{start_date} to {end_date}", 
                                style={'color': '#667eea', 'fontWeight': '600'}),
                        html.Span(f" ({len(filtered_df):,} rows)", 
                                style={'color': '#718096', 'marginLeft': '10px'})
                    ], style={'margin': '0', 'fontSize': '14px'})
                ], className='date-filter-card')
            )
    
    if current_df is not None:
        filtered_df = current_df.copy()
        return current_df.to_dict('records'), ""
    return data, ""

# Callback: Handle sidebar navigation clicks and update active state
@app.callback(
    [Output('main-tabs', 'value'),
     Output('nav-overview', 'className'),
     Output('nav-visualizations', 'className'),
     Output('nav-eda', 'className'),
     Output('nav-forecasting', 'className'),
     Output('nav-predictions', 'className'),
     Output('nav-insights', 'className'),
     Output('nav-data-table', 'className')],
    [Input('nav-overview', 'n_clicks'),
     Input('nav-visualizations', 'n_clicks'),
     Input('nav-eda', 'n_clicks'),
     Input('nav-forecasting', 'n_clicks'),
     Input('nav-predictions', 'n_clicks'),
     Input('nav-insights', 'n_clicks'),
     Input('nav-data-table', 'n_clicks')]
)
def update_tab_from_sidebar(overview_clicks, viz_clicks, eda_clicks, forecast_clicks, 
                            pred_clicks, insights_clicks, table_clicks):
    ctx = callback_context
    base_class = "list-group-item list-group-item-action"
    active_class = base_class + " active"
    
    if not ctx.triggered:
        return 'overview', active_class, base_class, base_class, base_class, base_class, base_class, base_class
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    tab_map = {
        'nav-overview': 'overview',
        'nav-visualizations': 'visualizations',
        'nav-eda': 'eda',
        'nav-forecasting': 'forecasting',
        'nav-predictions': 'predictions',
        'nav-insights': 'insights',
        'nav-data-table': 'data-table'
    }
    selected_tab = tab_map.get(button_id, 'overview')
    
    return (
        selected_tab,
        active_class if selected_tab == 'overview' else base_class,
        active_class if selected_tab == 'visualizations' else base_class,
        active_class if selected_tab == 'eda' else base_class,
        active_class if selected_tab == 'forecasting' else base_class,
        active_class if selected_tab == 'predictions' else base_class,
        active_class if selected_tab == 'insights' else base_class,
        active_class if selected_tab == 'data-table' else base_class
    )

# Callback: Update metrics and content
@app.callback(
    [Output('metrics-row', 'children'),
     Output('tab-content', 'children')],
    [Input('main-tabs', 'value'),
     Input('run-analysis', 'n_clicks'),
     Input('filtered-data-store', 'data')],
    [State('target-column', 'value'),
     State('date-column', 'value'),
     State('value-column', 'value'),
     State('data-store', 'data')]
)
def update_content(tab, n_clicks, filtered_data, target_col, date_col, value_col, original_data):
    global filtered_df
    
    # Use filtered data if available, otherwise original
    if filtered_data:
        df = pd.DataFrame(filtered_data)
        filtered_df = df
    elif original_data:
        df = pd.DataFrame(original_data)
        filtered_df = df
    else:
        df = current_df if current_df is not None else pd.DataFrame()
    
    if df is None or len(df) == 0:
        return [], html.Div([
            html.H3("No data loaded"),
            html.P("Please upload a CSV/Excel file to begin analysis")
        ])
    
    # Calculate metrics
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100 if df.shape[0] > 0 else 0
    
    # Create metric cards
    metrics = html.Div([
        html.Div([create_metric_card("fas fa-database", f"{len(df):,}", "Total Rows", "#667eea")], className='col-md-3'),
        html.Div([create_metric_card("fas fa-columns", f"{len(df.columns)}", "Total Columns", "#48bb78")], className='col-md-3'),
        html.Div([create_metric_card("fas fa-chart-line", f"{len(numeric_cols)}", "Numeric Columns", "#ed8936")], className='col-md-3'),
        html.Div([create_metric_card("fas fa-exclamation-triangle", f"{missing_pct:.1f}%", "Missing Data", "#f56565")], className='col-md-3')
    ], className='row')
    
    # Render tab content
    if tab == 'overview':
        content = OverviewTabView.render(df)
    elif tab == 'eda':
        if n_clicks > 0:
            try:
                analysis_results['eda'] = analyzer.analyze_and_plot(df, target_col, use_cache=True)
                content = EDATabView.render(analysis_results.get('eda', {}), df)
            except Exception as e:
                content = html.Div(f"Error in EDA: {str(e)}", style={'color': 'red'})
        else:
            content = EDATabView.render(analysis_results.get('eda', {}), df)
    elif tab == 'visualizations':
        content = VisualizationsTabView.render(df, target_col)
    elif tab == 'forecasting':
        if n_clicks > 0 and date_col and value_col:
            try:
                ts = forecaster.prepare_time_series(df, date_col, value_col)
                analysis_results['forecasting'] = forecaster.compare_forecasts(ts, FORECAST_HORIZON)
                content = ForecastingTabView.render(analysis_results.get('forecasting', {}))
            except Exception as e:
                content = html.Div(f"Error in forecasting: {str(e)}", style={'color': 'red'})
        else:
            content = ForecastingTabView.render(analysis_results.get('forecasting', {}))
    elif tab == 'predictions':
        if n_clicks > 0 and target_col:
            try:
                analysis_results['predictions'] = predictor.auto_train(df, target_col)
                content = PredictionsTabView.render(analysis_results.get('predictions', {}))
            except Exception as e:
                content = html.Div(f"Error in predictions: {str(e)}", style={'color': 'red'})
        else:
            content = PredictionsTabView.render(analysis_results.get('predictions', {}))
    elif tab == 'insights':
        if n_clicks > 0:
            try:
                analysis_results['insights'] = explorer.generate_insights(df, target_col)
                content = InsightsTabView.render(analysis_results.get('insights', {}))
            except Exception as e:
                content = html.Div(f"Error generating insights: {str(e)}", style={'color': 'red'})
        else:
            content = InsightsTabView.render(analysis_results.get('insights', {}))
    elif tab == 'data-table':
        content = DataTableView.render(df)
    else:
        content = html.Div("Select a tab")
    
    return metrics, content

# Note: This file is now a module. Use main.py as the entry point.
# To run dashboard: python main.py --mode dashboard
# Or: python main.py --dashboard (after analysis)
