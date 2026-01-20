"""
View templates for HTML generation
"""
from .eda_report_view import EDAReportView
from .dashboard_views import (
    OverviewTabView,
    EDATabView,
    VisualizationsTabView,
    ForecastingTabView,
    PredictionsTabView,
    InsightsTabView,
    DataTableView
)

__all__ = [
    'EDAReportView',
    'OverviewTabView',
    'EDATabView',
    'VisualizationsTabView',
    'ForecastingTabView',
    'PredictionsTabView',
    'InsightsTabView',
    'DataTableView'
]
