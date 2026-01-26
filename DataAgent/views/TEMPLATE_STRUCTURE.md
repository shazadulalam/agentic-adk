# Template Structure Documentation

## Overview

All hardcoded HTML has been separated from Python files and moved to HTML template files in the `views` folder. The Python code now loads these templates and injects data using variable substitution.

## File Structure

```
views/
├── dashboard_base.html          # Base HTML template with CSS
├── template_renderer.py         # Template loading and rendering utility
├── html_components.py          # Component generator (HTML → Dash components)
├── components/
│   ├── metric_card.html        # Metric card template
│   ├── upload_area.html        # Upload area template
│   └── date_filter.html        # Date filter template
└── dashboard_views.py          # View classes (uses templates)

```

## How It Works

### 1. Template Renderer (`template_renderer.py`)

The `TemplateRenderer` class loads HTML files and replaces variables:

```python
from views.template_renderer import get_renderer

renderer = get_renderer()
template = renderer.load_template('dashboard_base.html')
html_output = renderer.render('metric_card.html', 
                             icon_class='fas fa-database',
                             value='1000',
                             label='Total Rows')
```

**Variable Format**: `{{variable_name}}` in HTML templates

### 2. HTML Components (`html_components.py`)

Converts HTML templates to Dash components:

```python
from views.html_components import get_html_generator

html_gen = get_html_generator()

# Generate metric card
card = html_gen.metric_card('fas fa-database', '1000', 'Total Rows', '#667eea')

# Generate upload area
upload = html_gen.upload_area()

# Generate status badge
badge = html_gen.status_badge('Success!', 'success')
```

### 3. Template Files

#### `dashboard_base.html`
- Base HTML structure
- All CSS styles
- D3.js and Bootstrap scripts
- Dash placeholders: `{%metas%}`, `{%css%}`, `{%scripts%}`, etc.

#### `components/metric_card.html`
Template variables:
- `{{icon_class}}` - Font Awesome icon class
- `{{icon_color}}` - Icon color
- `{{value}}` - Metric value
- `{{label}}` - Metric label

#### `components/upload_area.html`
- Static HTML for upload area
- No variables needed

#### `components/date_filter.html`
- Static HTML for date filter
- No variables needed (handled by Dash components)

## Usage in Python Files

### Loading Base Template

```python
from views.template_renderer import get_renderer

renderer = get_renderer()
app.index_string = renderer.load_template('dashboard_base.html')
```

### Using HTML Components

```python
from views.html_components import get_html_generator

html_gen = get_html_generator()

# In layout
dcc.Upload(
    id='upload-data',
    children=html_gen.upload_area(),
    ...
)

# In callbacks
status = html_gen.status_badge("File loaded", 'success')
card = html_gen.metric_card('fas fa-database', '1000', 'Rows', '#667eea')
```

### Data Flow

1. **Python → Template**: Data passed via function parameters
2. **Template → HTML**: Variables replaced in template
3. **HTML → Dash**: Converted to Dash components
4. **Dash → Browser**: Rendered in browser

## Adding New Templates

### Step 1: Create HTML Template

Create `views/components/my_component.html`:

```html
<div class="my-component">
    <h3>{{title}}</h3>
    <p>{{description}}</p>
    <span>{{value}}</span>
</div>
```

### Step 2: Add Component Generator Method

In `views/html_components.py`:

```python
def my_component(self, title: str, description: str, value: str) -> html.Div:
    """Generate my component from template"""
    template = self.renderer.load_template('components/my_component.html')
    html_str = self.renderer.render_string(
        template,
        title=title,
        description=description,
        value=value
    )
    # Convert to Dash component
    return html.Div([
        html.H3(title),
        html.P(description),
        html.Span(value)
    ], className='my-component')
```

### Step 3: Use in Dashboard

```python
from views.html_components import get_html_generator

html_gen = get_html_generator()
component = html_gen.my_component('Title', 'Description', '100')
```

## Benefits

1. **Separation of Concerns**: HTML separated from Python logic
2. **Maintainability**: Easy to update HTML without touching Python
3. **Reusability**: Templates can be reused across components
4. **Readability**: Cleaner Python code
5. **Flexibility**: Easy to swap templates or add new ones

## Template Variables

### Naming Convention
- Use lowercase with underscores: `{{icon_class}}`, `{{metric_value}}`
- Be descriptive: `{{total_rows}}` not `{{tr}}`

### Data Types
- All variables are converted to strings
- Format numbers in Python before passing: `f"{value:,}"`

### Escaping
- HTML in variables is not escaped (use with caution)
- For user input, use Dash's built-in escaping

## Example: Complete Flow

### 1. HTML Template (`metric_card.html`)
```html
<div class="metric-card">
    <i class="{{icon_class}}" style="color: {{icon_color}};"></i>
    <div class="metric-value">{{value}}</div>
    <div class="metric-label">{{label}}</div>
</div>
```

### 2. Python Component Generator
```python
def metric_card(self, icon, value, label, color="#667eea"):
    return html.Div([
        html.I(className=icon, style={'color': color}),
        html.Div(str(value), className='metric-value'),
        html.Div(label, className='metric-label')
    ], className='metric-card')
```

### 3. Usage in Dashboard
```python
html_gen = get_html_generator()
card = html_gen.metric_card('fas fa-database', '1000', 'Total Rows')
```

## Migration Notes

All hardcoded HTML has been moved from:
- `dashboards/dashboard.py` → `views/dashboard_base.html`
- Component HTML → `views/components/*.html`
- Component generation → `views/html_components.py`

The Python files now use template loading and component generation instead of hardcoded HTML strings.

---

**Last Updated**: 2026-01-21
**Status**: ✅ All HTML separated from Python files
