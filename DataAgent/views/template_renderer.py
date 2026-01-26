"""
Template Renderer for HTML Templates
Loads HTML templates and injects data using variable substitution
"""
import os
from typing import Dict, Any, Optional
from pathlib import Path


class TemplateRenderer:
    """
    Simple template renderer that loads HTML files and replaces variables
    """
    
    def __init__(self, templates_dir: str = None):
        """
        Initialize template renderer
        
        Args:
            templates_dir: Directory containing HTML templates (default: views folder)
        """
        if templates_dir is None:
            # Get views directory
            current_file = Path(__file__).resolve()
            templates_dir = current_file.parent
        
        self.templates_dir = Path(templates_dir)
    
    def load_template(self, template_name: str) -> str:
        """
        Load HTML template from file
        
        Args:
            template_name: Name of template file (e.g., 'dashboard_base.html')
        
        Returns:
            Template content as string
        """
        template_path = self.templates_dir / template_name
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def render(self, template_name: str, **kwargs) -> str:
        """
        Render template with variables
        
        Args:
            template_name: Name of template file
            **kwargs: Variables to inject into template
        
        Returns:
            Rendered HTML string
        """
        template = self.load_template(template_name)
        
        # Replace variables in format {{variable_name}}
        for key, value in kwargs.items():
            placeholder = f"{{{{{key}}}}}"
            template = template.replace(placeholder, str(value))
        
        return template
    
    def render_string(self, template_string: str, **kwargs) -> str:
        """
        Render template string with variables
        
        Args:
            template_string: Template as string
            **kwargs: Variables to inject
        
        Returns:
            Rendered HTML string
        """
        for key, value in kwargs.items():
            placeholder = f"{{{{{key}}}}}"
            template_string = template_string.replace(placeholder, str(value))
        
        return template_string


# Global template renderer instance
_renderer = None

def get_renderer() -> TemplateRenderer:
    """Get global template renderer instance"""
    global _renderer
    if _renderer is None:
        _renderer = TemplateRenderer()
    return _renderer
