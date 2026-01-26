# Test Commands for DataAgent Project

## Quick Test - Full Pipeline

Run the complete analysis pipeline with the default dataset:

```bash
cd /home/forhad/Study/personal/projects/DataAgent && python main.py --data datasets/bq-results-covid-open-data.csv --mode full
```

## Comprehensive Test - All Features

Test all components including forecasting and predictions:

```bash
cd /home/forhad/Study/personal/projects/DataAgent && python main.py --data datasets/bq-results-covid-open-data.csv --target $(python -c "import pandas as pd; df = pd.read_csv('datasets/bq-results-covid-open-data.csv'); print(df.select_dtypes(include=['number']).columns[-1] if len(df.select_dtypes(include=['number']).columns) > 0 else df.columns[-1])") --mode full
```

## Individual Component Tests

### 1. Test All Agents (Recommended)
```bash
cd /home/forhad/Study/personal/projects/DataAgent && python agents/testAgent.py
```

### 2. EDA Only
```bash
cd /home/forhad/Study/personal/projects/DataAgent && python main.py --data datasets/bq-results-covid-open-data.csv --mode eda
```

### 3. Predictions Only
```bash
cd /home/forhad/Study/personal/projects/DataAgent && python main.py --data datasets/bq-results-covid-open-data.csv --mode predict --target $(python -c "import pandas as pd; df = pd.read_csv('datasets/bq-results-covid-open-data.csv'); cols = df.select_dtypes(include=['number']).columns.tolist(); print(cols[-1] if cols else df.columns[-1])")
```

### 4. Launch Dashboard
```bash
cd /home/forhad/Study/personal/projects/DataAgent && python main.py --dashboard --data datasets/bq-results-covid-open-data.csv
```

## One-Line Full Test Command

```bash
cd /home/forhad/Study/personal/projects/DataAgent && python main.py --data datasets/bq-results-covid-open-data.csv --mode full && echo "✓ Full pipeline completed! Check reports/ and models/ directories."
```
