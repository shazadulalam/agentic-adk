"""
EDA Report HTML View Template
"""
import os
from config import REPORTS_DIR


class EDAReportView:
    """View for generating EDA HTML reports"""
    
    @staticmethod
    def generate_html_report(df, results: dict) -> str:
        """Generate comprehensive HTML report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #3498db; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .metric {{ background-color: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .warning {{ background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 10px 0; }}
                .error {{ background-color: #f8d7da; padding: 10px; border-left: 4px solid #dc3545; margin: 10px 0; }}
                img {{ max-width: 100%; height: auto; margin: 20px 0; border: 1px solid #ddd; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Comprehensive Data Analysis Report</h1>
                
                <h2>Dataset Overview</h2>
                <div class="metric">
                    <strong>Shape:</strong> {results['basic_stats']['shape'][0]} rows × {results['basic_stats']['shape'][1]} columns<br>
                    <strong>Memory Usage:</strong> {results['basic_stats']['memory_usage_mb']:.2f} MB
                </div>
                
                <h2>Data Quality</h2>
                <div class="metric">
                    <strong>Duplicate Rows:</strong> {results['data_quality']['duplicate_rows']}
                </div>
                
                <h2>Missing Values</h2>
                <table>
                    <tr><th>Column</th><th>Missing Count</th><th>Missing Percentage</th></tr>
        """
        
        for col, count in results['data_quality']['missing_values'].items():
            pct = results['data_quality']['missing_percentage'][col]
            html_content += f"<tr><td>{col}</td><td>{count}</td><td>{pct:.2f}%</td></tr>"
        
        html_content += """
                </table>
                
                <h2>Statistical Summary</h2>
                <p>See detailed statistics in the distributions section below.</p>
                
                <h2>Visualizations</h2>
        """
        
        # Add images if they exist
        images = ['correlation_matrix.png', 'distributions.png', 'boxplots.png', 'target_analysis.png']
        for img in images:
            img_path = os.path.join(REPORTS_DIR, img)
            if os.path.exists(img_path):
                html_content += f'<h3>{img.replace("_", " ").replace(".png", "").title()}</h3>'
                html_content += f'<img src="{img}" alt="{img}">'
        
        html_content += """
                <h2>Distribution Analysis</h2>
                <table>
                    <tr><th>Column</th><th>Skewness</th><th>Kurtosis</th><th>Is Normal</th></tr>
        """
        
        for col, dist_info in results['distributions'].items():
            html_content += f"""
                <tr>
                    <td>{col}</td>
                    <td>{dist_info['skewness']:.3f}</td>
                    <td>{dist_info['kurtosis']:.3f}</td>
                    <td>{'Yes' if dist_info['is_normal'] else 'No'}</td>
                </tr>
            """
        
        html_content += """
                </table>
                
                <h2>Outlier Analysis</h2>
                <table>
                    <tr><th>Column</th><th>Outlier Count</th><th>Outlier Percentage</th></tr>
        """
        
        for col, outlier_info in results['outliers'].items():
            html_content += f"""
                <tr>
                    <td>{col}</td>
                    <td>{outlier_info['count']}</td>
                    <td>{outlier_info['percentage']:.2f}%</td>
                </tr>
            """
        
        html_content += """
                </table>
            </div>
        </body>
        </html>
        """
        
        report_path = os.path.join(REPORTS_DIR, "eda_report.html")
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        return report_path
