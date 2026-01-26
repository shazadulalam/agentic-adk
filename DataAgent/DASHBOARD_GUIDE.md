# DataAgent Dashboard Guide

## 🚀 Quick Start

### Run the Dashboard

```bash
cd /home/forhad/Study/personal/projects/DataAgent
python dashboards/dashboard.py
```

Or use the convenience script:
```bash
./run_dashboard.sh
```

### Access the Dashboard

Once started, open your web browser and navigate to:
- **http://localhost:8050**
- **http://127.0.0.1:8050**

## 📊 Dashboard Features

### 1. **Overview Tab** 📈
- **Data Statistics**: 
  - Total rows and columns
  - Memory usage
  - Missing values count and percentage
  - Numeric vs categorical column counts
- **Column Information**: Complete list of all columns with data types
- **Summary Statistics**: Statistical summary (mean, std, min, max, etc.) for numeric columns

### 2. **Exploratory Analysis Tab** 🔍
- **Data Quality Metrics**:
  - Duplicate rows count
  - Missing values count
  - Complete rows count
- **Distribution Analysis**: 
  - Mean, median, standard deviation
  - Skewness and kurtosis
  - Normality tests
- **Correlation Analysis**: Interactive correlation matrix heatmap
- **Outlier Detection**: Outlier counts and percentages per column
- **Generated Visualizations**: View saved correlation matrices, distributions, and box plots

### 3. **Visualizations Tab** 📊
- **Correlation Matrix**: Interactive heatmap showing relationships between features
- **Distribution Plots**: Histograms for numeric columns
- **Box Plots**: Outlier detection visualizations
- **Scatter Plots**: Top correlated feature pairs (for smaller datasets)

### 4. **Forecasting Tab** 🔮
- Time series forecasting results
- Multiple model comparisons (ARIMA, Prophet, LSTM)
- Forecast visualizations with confidence intervals

### 5. **Predictions Tab** 🤖
- **Model Comparison Table**: Side-by-side comparison of all trained models
  - Metrics: Accuracy, Precision, Recall, F1 (classification) or R², RMSE, MAE (regression)
  - Best model highlighted
- **Model Details**: 
  - Individual model metrics
  - Prediction vs Actual scatter plots
  - Performance visualizations

### 6. **Insights Tab** 💡
- **Data Quality Issues**: Warnings about missing data, duplicates, etc.
- **Patterns Detected**: Correlations, outliers, trends
- **Recommendations**: Suggestions for data preprocessing and modeling

### 7. **Data Table Tab** 📋
- Interactive data table with:
  - Pagination (20 rows per page)
  - Sorting capabilities
  - Filtering options
  - Shows first 1000 rows

## 🎨 Interface Design

The dashboard features a **clean, modern interface** with:
- **Gradient header** with purple theme
- **Card-based layouts** for metrics
- **Color-coded sections**:
  - Purple: Primary metrics
  - Green: Success/positive metrics
  - Yellow: Warnings
  - Blue: Information
- **Responsive design** that works on different screen sizes
- **Interactive Plotly graphs** with zoom, pan, and hover capabilities
- **Professional data tables** with sorting and filtering

## 📝 Usage Instructions

### Step 1: Load Data
1. **Option A**: Upload a CSV file using the drag-and-drop area
2. **Option B**: Use the default dataset (automatically loaded if available)

### Step 2: Configure Analysis
1. Select **Target Column** for predictions (required for prediction tab)
2. Select **Date Column** for forecasting (optional)
3. Select **Value Column** for forecasting (optional)

### Step 3: Run Analysis
1. Click **"🔄 Run Full Analysis"** button
2. Wait for processing to complete
3. Navigate through tabs to view results

### Step 4: Explore Results
- Switch between tabs to see different aspects of the analysis
- Interact with graphs (zoom, pan, hover)
- Sort and filter data tables
- Compare model performances

## 🔧 Technical Details

### Default Dataset
- Automatically loads `datasets/bq-results-covid-open-data.csv` if available
- Limited to first 10,000 rows for dashboard performance
- Full dataset available for command-line analysis

### Performance Optimizations
- EDA limited to top 30 columns to prevent memory issues
- Visualizations limited to top 20 columns
- Data sampling for large datasets
- Caching of EDA results

### Memory Safety
- Automatic sampling for datasets > 50,000 rows
- Feature limiting to prevent OOM errors
- Efficient data type conversions (float32)

## 🐛 Troubleshooting

### Dashboard won't start
- Check if port 8050 is already in use
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.7+)

### No data showing
- Upload a CSV file or ensure default dataset exists
- Check file format (must be CSV)
- Verify file is not corrupted

### Analysis fails
- Check target column is selected
- Ensure dataset has numeric columns
- Verify sufficient memory available
- Check error messages in browser console (F12)

### Graphs not displaying
- Check browser console for JavaScript errors
- Verify Plotly is installed: `pip install plotly`
- Try refreshing the page

## 📚 Additional Resources

- **Command-line usage**: See `README.md`
- **Memory optimizations**: See `MEMORY_OPTIMIZATIONS.md`
- **Test commands**: See `TEST_COMMANDS.md`

## 🎯 Best Practices

1. **Start with Overview**: Get familiar with your data first
2. **Run EDA**: Understand data quality and distributions
3. **Check Insights**: Review recommendations before modeling
4. **Compare Models**: Use the comparison table to select best model
5. **Visualize Results**: Use graphs to understand model performance

---

**Enjoy exploring your data with DataAgent! 🚀**
