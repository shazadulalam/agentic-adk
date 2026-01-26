"""
HTML Component Generator
Converts HTML templates to Dash components
"""
from dash import html, dcc
from .template_renderer import get_renderer
import os


class HTMLComponentGenerator:
    """
    Generates Dash HTML components from HTML template files
    """
    
    def __init__(self):
        self.renderer = get_renderer()
    
    def metric_card(self, icon: str, value: str, label: str, color: str = "#667eea") -> html.Div:
        """
        Generate metric card component from template
        
        Args:
            icon: Font Awesome icon class (e.g., 'fas fa-database')
            value: Metric value to display
            label: Metric label
            color: Icon color
        
        Returns:
            Dash HTML Div component
        """
        template = self.renderer.load_template('components/metric_card.html')
        html_str = self.renderer.render_string(
            template,
            icon_class=icon,
            icon_color=color,
            value=value,
            label=label
        )
        # Convert HTML string to Dash component
        # Note: Dash doesn't directly support HTML strings, so we use html.Div with dangerously_allow_html
        # For proper Dash components, we'll create them directly
        return html.Div([
            html.Div([
                html.I(className=icon, style={'fontSize': '48px', 'color': color, 'marginBottom': '15px'}),
                html.Div(str(value), className='metric-value'),
                html.Div(label, className='metric-label')
            ], style={'textAlign': 'center'})
        ], className='metric-card')
    
    def upload_area(self) -> html.Div:
        """Generate upload area component"""
        return html.Div([
            html.I(className="fas fa-cloud-upload-alt upload-icon"),
            html.P('Drag & Drop or Click to Upload', 
                  style={'fontSize': '16px', 'fontWeight': '600', 'color': '#4a5568', 'margin': '10px 0'}),
            html.P('CSV, XLSX, XLS files supported', 
                  style={'fontSize': '12px', 'color': '#718096'})
        ])
    
    def date_filter_section(self) -> list:
        """Generate date filter section component"""
        return [
            html.H5("📅 Date Range Filter", style={'marginBottom': '15px', 'fontWeight': '600'}),
            html.Label("Start Date:", style={'fontSize': '12px', 'fontWeight': '500', 'color': '#4a5568'}),
            dcc.DatePickerSingle(
                id='start-date',
                placeholder="Select start date",
                style={'width': '100%', 'marginBottom': '15px'}
            ),
            html.Label("End Date:", style={'fontSize': '12px', 'fontWeight': '500', 'color': '#4a5568'}),
            dcc.DatePickerSingle(
                id='end-date',
                placeholder="Select end date",
                style={'width': '100%', 'marginBottom': '15px'}
            ),
            html.Button("Apply Filter", id='apply-date-filter', n_clicks=0,
                       className='btn btn-primary btn-primary-custom',
                       style={'width': '100%', 'marginTop': '10px'}),
            html.Button("Clear Filter", id='clear-date-filter', n_clicks=0,
                       className='btn btn-outline-secondary',
                       style={'width': '100%', 'marginTop': '10px'})
        ]
    
    def status_badge(self, message: str, status: str = 'success') -> html.Div:
        """
        Generate status badge component
        
        Args:
            message: Status message
            status: 'success' or 'error'
        
        Returns:
            Dash HTML Div component
        """
        badge_class = 'status-badge status-success' if status == 'success' else 'status-badge status-error'
        return html.Div([
            html.Span(message, className=badge_class)
        ])


# Global instance
_html_generator = None

def get_html_generator() -> HTMLComponentGenerator:
    """Get global HTML component generator"""
    global _html_generator
    if _html_generator is None:
        _html_generator = HTMLComponentGenerator()
    return _html_generator
