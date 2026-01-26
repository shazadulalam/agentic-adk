# Caching System for EDA

## Overview

The DataAgent now includes intelligent caching for Exploratory Data Analysis (EDA) to avoid re-processing the same dataset multiple times.

## How It Works

1. **First Run**: When you run EDA for the first time on a dataset:
   - Full analysis is performed
   - Results are saved to cache (`reports/cache/`)
   - Visualizations are generated

2. **Subsequent Runs**: If you run EDA again on the same dataset:
   - Cache is checked automatically
   - If cached results exist, they are loaded instantly
   - No re-computation needed
   - Visualizations are only regenerated if missing

## Cache Key Generation

The cache key is based on:
- Dataset shape (rows × columns)
- Column names
- Sample data (first 100 rows)
- Target column name (if specified)

This ensures that if the dataset changes, a fresh analysis will be performed.

## Cache Location

- **Cache Directory**: `reports/cache/`
- **Cache Files**: `eda_<hash>_<target>.pkl`

## Benefits

- ⚡ **Faster Execution**: Step 3 (EDA) completes instantly on subsequent runs
- 💾 **Saves Resources**: No redundant computations
- 🔄 **Smart Updates**: Automatically detects dataset changes

## Usage

Caching is **enabled by default**. The analyzer automatically:
- Checks cache before processing
- Uses cached results if available
- Saves results after processing

### Disable Caching (if needed)

```python
from agents.analyzer import ModelAnalyzer

analyzer = ModelAnalyzer()
results = analyzer.analyze_and_plot(df, target_col, use_cache=False)
```

## Example

**First Run:**
```
[3/6] Running Exploratory Data Analysis...
  Performing fresh EDA analysis...
✓ EDA results cached for future use
✓ EDA completed. Reports saved to reports/ directory
```

**Second Run (same dataset):**
```
[3/6] Running Exploratory Data Analysis...
✓ Using cached EDA results (dataset already analyzed - skipping computation)
  All visualizations already exist
✓ EDA completed. Reports saved to reports/ directory
```

## Cache Management

- Cache files are stored in `reports/cache/`
- To clear cache: Delete files in `reports/cache/` directory
- Cache persists between runs
- Each unique dataset gets its own cache file

## Notes

- Cache is based on dataset content, so changing the dataset will trigger fresh analysis
- Visualizations are checked separately - missing ones are regenerated
- Cache works across different target columns (separate cache per target)
