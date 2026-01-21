"""
Dashboard Layout - All HTML/UI code separated from main.py
"""
from dash import html, dcc
from views.html_components import get_html_generator


def create_dashboard_layout():
    """
    Create and return the complete dashboard layout
    All HTML code is here, separated from main.py
    """
    html_gen = get_html_generator()
    
    layout = html.Div([
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
                    html.H4("📁 Data Source", style={'marginBottom': '20px', 'fontWeight': '600'}),
                    
                    # File Upload
                    dcc.Upload(
                        id='upload-data',
                        children=html_gen.upload_area(),
                        style={'width': '100%'},
                        multiple=False
                    ),
                    
                    html.Div(id='upload-status', style={'marginTop': '15px'}),
                    
                    html.Hr(style={'margin': '25px 0'}),
                    
                    # Date Range Filter
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
                    # Metrics Cards Row
                    html.Div(id='metrics-row', className='row', style={'marginBottom': '30px'}),
                    
                    # Date Range Display
                    html.Div(id='date-range-display', style={'marginBottom': '20px'}),
                    
                    # Tabs
                    dcc.Tabs(id='main-tabs', value='overview', children=[
                        dcc.Tab(label='📈 Overview', value='overview', 
                               style={'fontWeight': '600'}, selected_style={'fontWeight': '700'}),
                        dcc.Tab(label='📊 Visualizations', value='visualizations',
                               style={'fontWeight': '600'}, selected_style={'fontWeight': '700'}),
                        dcc.Tab(label='🔍 EDA Analysis', value='eda',
                               style={'fontWeight': '600'}, selected_style={'fontWeight': '700'}),
                        dcc.Tab(label='🔮 Forecasting', value='forecasting',
                               style={'fontWeight': '600'}, selected_style={'fontWeight': '700'}),
                        dcc.Tab(label='🤖 Predictions', value='predictions',
                               style={'fontWeight': '600'}, selected_style={'fontWeight': '700'}),
                        dcc.Tab(label='💡 Insights', value='insights',
                               style={'fontWeight': '600'}, selected_style={'fontWeight': '700'}),
                        dcc.Tab(label='📋 Data Table', value='data-table',
                               style={'fontWeight': '600'}, selected_style={'fontWeight': '700'})
                    ], style={'marginBottom': '20px'}),
                    
                    # Tab Content
                    html.Div(id='tab-content', className='tab-content-wrapper')
                    
                ], className='col-md-9')
            ], className='row', style={'padding': '20px'})
        ], className='container-fluid')
    ])
    
    return layout
