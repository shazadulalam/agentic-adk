from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

COLORS = {
    'primary': '#667eea',
    'success': '#48bb78',
    'warning': '#ed8936',
    'danger': '#f56565',
    'info': '#9f7aea',
    'secondary': '#38b2ac'
}

def create_metric_card(icon, value, label, color=COLORS['primary']):
    """Create a metric card component"""
    return html.Div([
        html.Div([
            html.I(className=icon, style={'fontSize': '32px', 'color': color, 'marginBottom': '10px'}),
            html.H4(label, style={'margin': '10px 0'}),
            html.P(str(value), style={'fontSize': '36px', 'fontWeight': 'bold', 'color': color, 'margin': '0'})
        ], style={'textAlign': 'center'})
    ], style={
        'background': 'white',
        'padding': '30px',
        'borderRadius': '12px',
        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
        'margin': '10px',
        'flex': '1',
        'minWidth': '200px',
        'border': f'2px solid {color}'
    })

def create_section_header(title, icon='', color=COLORS['primary']):
    """Create a section header"""
    return html.H2(f"{icon} {title}", style={'marginBottom': '20px', 'color': color, 'fontWeight': 'bold'})

def create_card(content, color=COLORS['primary']):
    """Create a styled card"""
    return html.Div(content, style={
        'padding': '20px',
        'backgroundColor': 'white',
        'borderRadius': '8px',
        'marginBottom': '20px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'border': f'1px solid {color}'
    })

def create_bar_chart(df, col, title=None, color=COLORS['primary']):
    """Create a bar chart"""
    if df[col].dtype in ['object', 'category']:
        value_counts = df[col].value_counts().head(10)
        fig = px.bar(x=value_counts.index.astype(str), y=value_counts.values,
                   title=title or f"{col} Distribution",
                   labels={'x': col, 'y': 'Count'},
                   color_discrete_sequence=[color])
    else:
        fig = px.histogram(df, x=col, nbins=20, title=title or f"{col} Distribution",
                         color_discrete_sequence=[color])
    fig.update_layout(height=300, template='plotly_white', margin=dict(l=10, r=10, t=40, b=10))
    return dcc.Graph(figure=fig)

def create_line_chart(df, x_col, y_col, title=None):
    """Create a line chart"""
    fig = px.line(df, x=x_col, y=y_col, title=title or f"{y_col} over {x_col}")
    fig.update_layout(height=300, template='plotly_white')
    return dcc.Graph(figure=fig)
