"""Dashboard view components for Dash application"""
from dash import html, dcc, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.common import setup_path, get_numeric_cols, get_categorical_cols, calc_missing_pct
from utils.dashboard_components import create_metric_card, create_card, create_bar_chart, COLORS
setup_path()
from feature_engineering import FeatureEngineeringStrategies
from utils.neo4j_graph import Neo4jGraphBuilder
from utils.segmentation import SegmentationAnalyzer


class OverviewTabView:
    """View for overview tab with comprehensive data statistics"""
    
    @staticmethod
    def render(df: pd.DataFrame):
        """Render overview tab content with enhanced metrics"""
        numeric_cols = get_numeric_cols(df)
        categorical_cols = get_categorical_cols(df)
        missing_pct = calc_missing_pct(df)
        
        metrics = [
            create_metric_card("fas fa-database", f"{df.shape[0]:,}", "Rows", COLORS['primary']),
            create_metric_card("fas fa-memory", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f}", "MB", COLORS['success']),
            create_metric_card("fas fa-exclamation-triangle", f"{df.isnull().sum().sum():,}", f"Missing ({missing_pct:.1f}%)", COLORS['warning']),
            create_metric_card("fas fa-chart-bar", len(numeric_cols), f"Numeric ({len(categorical_cols)} Cat)", COLORS['info'])
        ]
        
        # Summary statistics for numeric columns
        summary_stats = []
        if len(numeric_cols) > 0:
            summary_df = df[numeric_cols].describe().T.reset_index()
            summary_df.columns = ['Column'] + [col for col in summary_df.columns[1:]]
            summary_stats = summary_df.to_dict('records')
        
        seg_analyzer = SegmentationAnalyzer()
        seg_summary = seg_analyzer.get_segmentation_summary(df)
        
        return html.Div([
            html.Div([
                html.H2("📊 Dataset Overview", style={'marginBottom': '20px', 'color': '#333'}),
                html.Div(metrics, style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around', 'marginBottom': '30px'}),
            ]),
            html.Hr(style={'margin': '30px 0'}),
            OverviewTabView._render_segmentation_summary(seg_summary),
            html.Hr(style={'margin': '30px 0'}),
            OverviewTabView._render_feature_engineering_strategies()
        ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})
    
    @staticmethod
    def _render_segmentation_summary(seg_summary: dict):
        """Render segmentation summary cards"""
        seg_types = {
            'demographic': {'icon': '👥', 'color': '#667eea', 'title': 'Demographic'},
            'geographic': {'icon': '🌍', 'color': '#48bb78', 'title': 'Geographic'},
            'firmographic': {'icon': '🏢', 'color': '#ed8936', 'title': 'Firmographic'},
            'behavioral': {'icon': '🛒', 'color': '#f56565', 'title': 'Behavioral'},
            'technographic': {'icon': '💻', 'color': '#9f7aea', 'title': 'Technographic'},
            'psychographic': {'icon': '🧠', 'color': '#38b2ac', 'title': 'Psychographic'}
        }
        
        cards = []
        for seg_type, info in seg_types.items():
            count = seg_summary.get(seg_type, {}).get('count', 0)
            cards.append(html.Div([
                html.Div([
                    html.Div([
                        html.Span(info['icon'], style={'fontSize': '32px', 'marginBottom': '10px'}),
                        html.H5(info['title'], style={'color': '#333', 'margin': '10px 0', 'fontSize': '16px'}),
                        html.P(f"{count} columns", style={'fontSize': '24px', 'fontWeight': 'bold', 'color': info['color'], 'margin': '0'})
                    ], style={'textAlign': 'center', 'padding': '20px'})
                ], className='card', style={
                    'border': f'2px solid {info["color"]}',
                    'borderRadius': '12px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'backgroundColor': 'white',
                    'height': '100%'
                })
            ], className='col-md-4 col-lg-2', style={'marginBottom': '15px'}))
        
        return html.Div([
            html.H2("🎯 Data Segmentation Summary", style={'color': '#333', 'marginBottom': '20px', 'fontWeight': 'bold'}),
            html.P("Automatically detected segmentation types in your dataset", style={'color': '#666', 'fontSize': '14px', 'marginBottom': '20px'}),
            html.Div(cards, className='row')
        ])
    
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
            seg_analyzer = SegmentationAnalyzer()
            seg_summary = seg_analyzer.get_segmentation_summary(df)
            return EDATabView._render_segmentation_only(seg_summary, df)
        
        content = [html.H2("📊 Exploratory Data Analysis Results", style={'marginBottom': '20px', 'color': '#333'})]
        
        if 'data_quality' in results:
            content.append(html.H3("Data Quality", style={'marginTop': '20px', 'color': '#667eea'}))
            quality = results['data_quality']
            content.append(html.Div([
                html.P(f"Duplicate Rows: {quality.get('duplicate_rows', 0)}", style={'margin': '5px 0'}),
                html.P(f"Missing Values: {quality.get('missing_values', 0)}", style={'margin': '5px 0'}),
                html.P(f"Complete Rows: {quality.get('complete_rows', 0)}", style={'margin': '5px 0'})
            ], style={'padding': '15px', 'backgroundColor': 'white', 'borderRadius': '8px', 'marginBottom': '20px'}))
        
        if 'distributions' in results:
            content.append(html.H3("Distribution Analysis", style={'marginTop': '20px', 'color': '#667eea'}))
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
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': '#667eea', 'color': 'white', 'fontWeight': 'bold'},
                style_data={'backgroundColor': 'white'}
            ))
        
        if 'segmentation' in results:
            content.append(EDATabView._render_segmentation_section(results['segmentation'], df))
        else:
            seg_analyzer = SegmentationAnalyzer()
            seg_summary = seg_analyzer.get_segmentation_summary(df)
            content.append(EDATabView._render_segmentation_section(seg_summary, df))
        
        return html.Div(content, style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})
    
    @staticmethod
    def _render_segmentation_section(segmentation: dict, df: pd.DataFrame):
        """Render segmentation analysis section"""
        seg_analyzer = SegmentationAnalyzer()
        seg_types = {
            'demographic': {'icon': '👥', 'color': '#667eea', 'title': 'Demographic Segmentation'},
            'geographic': {'icon': '🌍', 'color': '#48bb78', 'title': 'Geographic Segmentation'},
            'firmographic': {'icon': '🏢', 'color': '#ed8936', 'title': 'Firmographic Segmentation'},
            'behavioral': {'icon': '🛒', 'color': '#f56565', 'title': 'Behavioral Segmentation'},
            'technographic': {'icon': '💻', 'color': '#9f7aea', 'title': 'Technographic Segmentation'},
            'psychographic': {'icon': '🧠', 'color': '#38b2ac', 'title': 'Psychographic Segmentation'}
        }
        
        content = [html.H3("🎯 Data Segmentation Analysis", style={'marginTop': '30px', 'marginBottom': '20px', 'color': '#333'})]
        
        for seg_type, info in seg_types.items():
            if seg_type in segmentation and segmentation[seg_type]['count'] > 0:
                seg_data = segmentation[seg_type]
                content.append(html.Div([
                    html.Div([
                        html.H4([
                            html.Span(info['icon'], style={'marginRight': '10px', 'fontSize': '24px'}),
                            info['title']
                        ], style={'color': info['color'], 'marginBottom': '15px'}),
                        html.P(f"Columns Found: {seg_data['count']}", style={'fontSize': '14px', 'color': '#666', 'marginBottom': '10px'}),
                        html.Div([
                            html.Span(col, className='badge', style={
                                'backgroundColor': info['color'],
                                'color': 'white',
                                'padding': '5px 10px',
                                'margin': '3px',
                                'borderRadius': '4px',
                                'fontSize': '12px'
                            }) for col in seg_data['columns'][:10]
                        ], style={'marginBottom': '15px'}),
                        EDATabView._render_segmentation_charts(df, seg_type, seg_data['columns'])
                    ], style={
                        'padding': '20px',
                        'backgroundColor': 'white',
                        'borderRadius': '8px',
                        'marginBottom': '20px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                    })
                ]))
        
        return html.Div(content)
    
    @staticmethod
    def _render_segmentation_charts(df: pd.DataFrame, seg_type: str, columns: list):
        """Render charts for segmentation columns"""
        charts = [create_bar_chart(df, col) for col in columns[:3] if col in df.columns]
        return html.Div(charts, className='row', style={'marginTop': '15px'}) if charts else html.Div()
    
    @staticmethod
    def _render_segmentation_only(segmentation: dict, df: pd.DataFrame):
        """Render only segmentation when no EDA results available"""
        content = [
            html.H2("📊 Data Segmentation Analysis", style={'marginBottom': '20px', 'color': '#333'}),
            html.P("Run Full Analysis for complete EDA results", style={'color': '#666', 'marginBottom': '30px'})
        ]
        content.append(EDATabView._render_segmentation_section(segmentation, df))
        return html.Div(content, style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})


class VisualizationsTabView:
    """View for visualizations tab with interactive graphs"""
    
    @staticmethod
    def render(df: pd.DataFrame, target_col: str = None):
        """Render visualizations tab content with enhanced graphs"""
        numeric_cols = get_numeric_cols(df).tolist()
        
        if not numeric_cols:
            return create_card([
                html.I(className="fas fa-chart-bar", style={'fontSize': '48px', 'color': COLORS['primary'], 'marginBottom': '20px'}),
                html.H3("No Numeric Columns Available", style={'color': '#333'}),
                html.P("Upload a dataset with numeric columns to see visualizations", style={'color': '#666', 'fontSize': '16px'})
            ], COLORS['primary'])
        
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
        
        def _create_chart_wrapper(fig, title):
            return html.Div([dcc.Graph(figure=fig.update_layout(height=300, template='plotly_white'))],
                          style={'marginBottom': '20px', 'background': 'white', 'padding': '15px', 
                                'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
        
        if numeric_cols:
            content.append(html.Div([
                html.H3("📈 Distribution Plots", style={'marginBottom': '15px', 'color': '#333'}),
                html.Div([_create_chart_wrapper(px.histogram(df, x=col, nbins=30, title=f"Distribution of {col}"), col)
                         for col in numeric_cols[:9]])
            ], style={'marginBottom': '30px'}))
            
            content.append(html.Div([
                html.H3("📦 Box Plots (Outlier Detection)", style={'marginBottom': '15px', 'color': '#333'}),
                html.Div([_create_chart_wrapper(px.box(df, y=col, title=f"Box Plot: {col}"), col)
                         for col in numeric_cols[:9]])
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


class GraphVisualizationTabView:
    """View for graph visualization using Neo4j concepts"""
    
    @staticmethod
    def render(df: pd.DataFrame):
        """Render graph visualization tab content"""
        graph_builder = Neo4jGraphBuilder()
        content = [html.H2("🕸️ Graph Visualization & Data Relationships", style={'marginBottom': '20px', 'color': '#333'})]
        
        if df.empty or len(df) == 0:
            content.append(html.Div([
                html.P("No data loaded. Showing sample graph visualization.", 
                      style={'color': '#666', 'marginBottom': '20px', 'fontStyle': 'italic'}),
                GraphVisualizationTabView._create_sample_graph()
            ]))
            graph_builder.close()
            return html.Div(content, style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})
        
        corr_graph = graph_builder.build_correlation_graph(df, threshold=0.5)
        feature_graph = graph_builder.build_feature_relationship_graph(df, top_n=15)
        
        if corr_graph['nodes']:
            content.append(html.H3("📊 Feature Correlation Network", style={'marginTop': '30px', 'color': '#667eea'}))
            content.append(GraphVisualizationTabView._create_network_graph(corr_graph, "Correlation Network"))
        elif len(df.select_dtypes(include=[np.number]).columns) >= 2:
            corr_graph = graph_builder.build_correlation_graph(df, threshold=0.3)
            if corr_graph['nodes']:
                content.append(html.H3("📊 Feature Correlation Network", style={'marginTop': '30px', 'color': '#667eea'}))
                content.append(GraphVisualizationTabView._create_network_graph(corr_graph, "Correlation Network"))
        
        if feature_graph['nodes']:
            content.append(html.H3("🔗 Feature Relationship Graph", style={'marginTop': '30px', 'color': '#667eea'}))
            content.append(GraphVisualizationTabView._create_network_graph(feature_graph, "Feature Relationships"))
        
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if categorical_cols and numeric_cols:
            segment_col = categorical_cols[0]
            value_col = numeric_cols[0] if numeric_cols else None
            if value_col:
                seg_graph = graph_builder.build_segmentation_graph(df, segment_col, value_col)
                if seg_graph['nodes']:
                    content.append(html.H3("📈 Data Segmentation", style={'marginTop': '30px', 'color': '#667eea'}))
                    content.append(GraphVisualizationTabView._create_segmentation_viz(df, segment_col, value_col))
        
        if len(content) == 1:
            content.append(html.Div([
                html.P("No strong correlations found. Showing sample graph visualization.", 
                      style={'color': '#666', 'marginBottom': '20px', 'fontStyle': 'italic'}),
                GraphVisualizationTabView._create_sample_graph()
            ]))
        
        graph_builder.close()
        return html.Div(content, style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'minHeight': '100vh'})
    
    @staticmethod
    def _create_sample_graph():
        """Create a sample graph visualization"""
        sample_nodes = [
            {'id': 'Feature_A', 'label': 'Feature A', 'type': 'feature'},
            {'id': 'Feature_B', 'label': 'Feature B', 'type': 'feature'},
            {'id': 'Feature_C', 'label': 'Feature C', 'type': 'feature'},
            {'id': 'Feature_D', 'label': 'Feature D', 'type': 'feature'},
            {'id': 'Feature_E', 'label': 'Feature E', 'type': 'feature'}
        ]
        sample_edges = [
            {'source': 'Feature_A', 'target': 'Feature_B', 'weight': 0.85, 'type': 'correlation'},
            {'source': 'Feature_B', 'target': 'Feature_C', 'weight': 0.72, 'type': 'correlation'},
            {'source': 'Feature_C', 'target': 'Feature_D', 'weight': 0.68, 'type': 'correlation'},
            {'source': 'Feature_A', 'target': 'Feature_E', 'weight': 0.65, 'type': 'correlation'},
            {'source': 'Feature_D', 'target': 'Feature_E', 'weight': 0.58, 'type': 'correlation'}
        ]
        sample_graph = {'nodes': sample_nodes, 'edges': sample_edges}
        return GraphVisualizationTabView._create_network_graph(sample_graph, "Sample Feature Network")
    
    @staticmethod
    def _create_network_graph(graph_data: dict, title: str):
        """Create Plotly network graph from graph data"""
        nodes = graph_data['nodes']
        edges = graph_data['edges']
        
        if not nodes:
            return html.Div("No graph data available")
        
        import math
        n = len(nodes)
        angle_step = 2 * math.pi / n if n > 0 else 0
        radius = 3
        
        node_positions = {}
        for i, node in enumerate(nodes):
            angle = i * angle_step
            node_positions[node['id']] = (radius * math.cos(angle), radius * math.sin(angle))
        
        edge_x, edge_y = [], []
        for edge in edges:
            if edge['source'] in node_positions and edge['target'] in node_positions:
                x0, y0 = node_positions[edge['source']]
                x1, y1 = node_positions[edge['target']]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
        
        node_x = [node_positions[node['id']][0] for node in nodes]
        node_y = [node_positions[node['id']][1] for node in nodes]
        node_text = [node['label'][:15] for node in nodes]
        node_info = [f"{node['label']}<br>Type: {node.get('type', 'node')}" for node in nodes]
        
        edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=1.5, color='#888'), 
                               hoverinfo='none', mode='lines')
        node_trace = go.Scatter(x=node_x, y=node_y, mode='markers+text', text=node_text,
                               textposition="middle center", hovertext=node_info, hoverinfo='text',
                               marker=dict(size=25, color='#667eea', line=dict(width=2, color='white')))
        
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(title=title, showlegend=False, hovermode='closest',
                                       margin=dict(b=20, l=5, r=5, t=40),
                                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                       height=500, plot_bgcolor='white'))
        
        return dcc.Graph(figure=fig, style={'background': 'white', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '20px'})
    
    @staticmethod
    def _create_segmentation_viz(df: pd.DataFrame, segment_col: str, value_col: str):
        """Create segmentation visualization"""
        segment_stats = df.groupby(segment_col)[value_col].agg(['mean', 'count', 'std']).reset_index()
        segment_stats = segment_stats.sort_values('mean', ascending=False).head(10)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=segment_stats[segment_col].astype(str), 
                            y=segment_stats['mean'],
                            error_y=dict(type='data', array=segment_stats['std']),
                            marker_color='#667eea',
                            text=segment_stats['count'].astype(str),
                            textposition='outside',
                            name='Average'))
        
        fig.update_layout(title=f"Segmentation Analysis: {value_col} by {segment_col}",
                         xaxis_title=segment_col, yaxis_title=f"Average {value_col}",
                         height=400, template='plotly_white')
        
        return dcc.Graph(figure=fig, style={'background': 'white', 'padding': '15px', 'borderRadius': '8px'})


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
