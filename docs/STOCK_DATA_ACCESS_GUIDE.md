# Stock Data Access and Analysis System

## Overview

This system provides comprehensive data access and analysis capabilities for stock CSV files. It consists of two main classes:

1. **StockDataReader** - Advanced data retrieval with flexible filtering
2. **StockDataAnalyzer** - Statistical analysis and technical indicators

## Installation

All operations should be performed in the `mkt` conda environment:

```bash
conda activate mkt
```

## Quick Start

```python
from src.data_fetch.stock_data_reader import StockDataReader
from src.data_fetch.stock_data_analyzer import StockDataAnalyzer

# Load stock data
reader = StockDataReader('data/raw/3MINDIA.csv')

# Get data for analysis
data = reader.get_date_range('2024-01-01', '2024-12-31')

# Analyze the data
analyzer = StockDataAnalyzer(data)
avg_price = analyzer.average('Close')
max_price = analyzer.max_value('Close')
sma_20 = analyzer.simple_moving_average('Close', window=20)
```

## StockDataReader - Data Retrieval

### Features

The `StockDataReader` class provides the following data retrieval methods:

#### 1. Get Complete or Partial Data

```python
reader = StockDataReader('data/raw/3MINDIA.csv')

# Get all columns
all_data = reader.get_columns()

# Get specific columns
price_data = reader.get_columns(['Date', 'Close', 'Volume'])
```

#### 2. Date Range Filtering

```python
# Get data for a specific date range
data = reader.get_date_range('2024-01-01', '2024-12-31')

# Get data with specific columns
data = reader.get_date_range('2024-01-01', '2024-12-31', 
                             columns=['Date', 'Close', 'Volume'])
```

#### 3. Data from a Specific Date

```python
# Get all data from a date onwards
data = reader.get_from_date('2024-01-01')

# Get data for a specific date
single_day = reader.get_on_date('2024-01-15')
```

#### 4. Lookback Period Retrieval

```python
# Get data for a date and previous 10 trading days
data = reader.get_lookback('2024-01-31', days=10)

# Get previous 30 days
data = reader.get_lookback('2024-01-31', days=30)

# Exclude the reference date
data = reader.get_lookback('2024-01-31', days=10, include_from_date=False)
```

#### 5. Time Period Filtering

**By Year:**
```python
# Get data for 2024
data_2024 = reader.get_by_year(2024)

# Get data for multiple years
data = reader.get_by_year([2023, 2024])

# Get all years
all_data = reader.get_by_year('all')
```

**By Quarter:**
```python
# Get Q1 2024 data
q1_data = reader.get_by_quarter(2024, 1)

# Get Q1 and Q2 2024
data = reader.get_by_quarter(2024, [1, 2])

# Get all quarters of 2024
data = reader.get_by_quarter(2024, 'all')
```

**By Month:**
```python
# Get January 2024 data
jan_data = reader.get_by_month(2024, 1)

# Get Jan-Mar 2024
data = reader.get_by_month(2024, [1, 2, 3])

# Get all months of 2024
data = reader.get_by_month(2024, 'all')
```

**By Week:**
```python
# Get week 1 of 2024
week1_data = reader.get_by_week(2024, 1)

# Get first 4 weeks of 2024
data = reader.get_by_week(2024, [1, 2, 3, 4])
```

#### 6. Stock Information

```python
# Get summary information
info = reader.get_info()
print(info)
# Output:
# {
#     'symbol': '3MINDIA',
#     'total_records': 4939,
#     'date_range': {'start': '2005-12-01', 'end': '2024-11-30'},
#     'years_available': [2005, 2006, ..., 2024],
#     'columns': ['Date', 'Price', 'Close', 'High', 'Low', 'Open', 'Volume']
# }
```

## StockDataAnalyzer - Data Analysis

### Features

The `StockDataAnalyzer` class provides comprehensive analysis capabilities:

#### 1. Basic Statistics

```python
analyzer = StockDataAnalyzer(data)

# Calculate average
avg_close = analyzer.average('Close')
avg_volume = analyzer.average('Volume')

# Get maximum value with date
max_close = analyzer.max_value('Close')
# Returns: {'value': 1500.5, 'date': '2024-01-15', 'index': 42}

# Get minimum value with date
min_close = analyzer.min_value('Close')
# Returns: {'value': 1200.5, 'date': '2024-03-15', 'index': 15}

# Other statistics
median = analyzer.median('Close')
std_dev = analyzer.std_dev('Close')
variance = analyzer.variance('Close')

# Percentiles
p25 = analyzer.percentile('Close', 0.25)  # 25th percentile
p75 = analyzer.percentile('Close', 0.75)  # 75th percentile

# Comprehensive summary
stats = analyzer.summary_stats('Close')
# Returns: {'count', 'mean', 'median', 'std', 'min', 'max', 'q25', 'q75', 'range'}
```

#### 2. Moving Averages

**Simple Moving Average (SMA):**
```python
# Calculate SMA
sma_20 = analyzer.simple_moving_average('Close', window=20)
sma_50 = analyzer.simple_moving_average('Close', window=50)
sma_200 = analyzer.simple_moving_average('Close', window=200)

# Add to dataframe
sma_20 = analyzer.simple_moving_average('Close', window=20, add_to_data=True)
```

**Exponential Moving Average (EMA):**
```python
# Calculate EMA
ema_12 = analyzer.exponential_moving_average('Close', span=12)
ema_26 = analyzer.exponential_moving_average('Close', span=26)

# Add to dataframe
ema_12 = analyzer.exponential_moving_average('Close', span=12, add_to_data=True)
```

**Weighted Moving Average (WMA):**
```python
wma_20 = analyzer.weighted_moving_average('Close', window=20)
```

**Cumulative Moving Average (CMA):**
```python
cma = analyzer.cumulative_moving_average('Close')
```

#### 3. Returns Calculations

```python
# Daily returns (percentage)
daily_returns = analyzer.returns('Close', periods=1)

# Weekly returns
weekly_returns = analyzer.returns('Close', periods=5)

# Absolute change
abs_change = analyzer.returns('Close', periods=1, percentage=False)

# Logarithmic returns
log_returns = analyzer.log_returns('Close', periods=1)

# Cumulative returns
cum_returns = analyzer.cumulative_returns('Close')
```

#### 4. Volatility Analysis

```python
# Rolling volatility
vol_20 = analyzer.volatility('Close', window=20)

# Annualized volatility (assumes 252 trading days)
annual_vol = analyzer.volatility('Close', window=20, annualize=True)

# Add to dataframe
vol = analyzer.volatility('Close', window=20, add_to_data=True)
```

#### 5. Range and Spread

```python
# Daily range (High - Low)
daily_range = analyzer.daily_range()
avg_range = daily_range.mean()

# Average True Range (ATR)
atr_14 = analyzer.average_true_range(window=14)
```

#### 6. Working with Results

```python
# Get the dataframe with all added columns
result_data = analyzer.get_data()

# Reset analyzer with new data
analyzer.reset_data(new_data)
```

## Complete Examples

### Example 1: Comprehensive Stock Analysis

```python
from src.data_fetch.stock_data_reader import StockDataReader
from src.data_fetch.stock_data_analyzer import StockDataAnalyzer

# Load stock data
reader = StockDataReader('data/raw/3MINDIA.csv')

# Get 2024 data
data_2024 = reader.get_by_year(2024)

# Analyze
analyzer = StockDataAnalyzer(data_2024)

# Basic statistics
print(f"Average Close: {analyzer.average('Close'):.2f}")
print(f"Max Close: {analyzer.max_value('Close')}")
print(f"Min Close: {analyzer.min_value('Close')}")

# Moving averages
sma_20 = analyzer.simple_moving_average('Close', window=20, add_to_data=True)
sma_50 = analyzer.simple_moving_average('Close', window=50, add_to_data=True)
ema_12 = analyzer.exponential_moving_average('Close', span=12, add_to_data=True)

# Volatility
vol = analyzer.volatility('Close', window=20, add_to_data=True)

# Get results
results = analyzer.get_data()
print(results[['Date', 'Close', 'SMA_20', 'SMA_50', 'EMA_12']].tail())
```

### Example 2: Quarter-over-Quarter Comparison

```python
reader = StockDataReader('data/raw/3MINDIA.csv')

for quarter in [1, 2, 3, 4]:
    q_data = reader.get_by_quarter(2024, quarter)
    analyzer = StockDataAnalyzer(q_data)
    
    avg_close = analyzer.average('Close')
    max_info = analyzer.max_value('Close')
    min_info = analyzer.min_value('Close')
    
    print(f"Q{quarter} 2024:")
    print(f"  Average: {avg_close:.2f}")
    print(f"  High: {max_info['value']:.2f} on {max_info['date']}")
    print(f"  Low: {min_info['value']:.2f} on {min_info['date']}")
```

### Example 3: Recent Performance Analysis

```python
reader = StockDataReader('data/raw/3MINDIA.csv')

# Get last 30 trading days
recent_data = reader.get_lookback('2024-11-30', days=30)

# Analyze
analyzer = StockDataAnalyzer(recent_data)

# Calculate metrics
daily_returns = analyzer.returns('Close', periods=1)
volatility = analyzer.volatility('Close', window=20)
sma_10 = analyzer.simple_moving_average('Close', window=10)

print(f"30-Day Performance:")
print(f"  Average Return: {daily_returns.mean():.2f}%")
print(f"  Volatility: {volatility.iloc[-1]:.2f}%")
print(f"  Current vs SMA-10: {recent_data['Close'].iloc[-1] / sma_10.iloc[-1] - 1:.2%}")
```

### Example 4: Year-over-Year Comparison

```python
reader = StockDataReader('data/raw/3MINDIA.csv')

for year in [2022, 2023, 2024]:
    year_data = reader.get_by_year(year)
    if len(year_data) > 0:
        analyzer = StockDataAnalyzer(year_data)
        
        stats = analyzer.summary_stats('Close')
        cum_return = analyzer.cumulative_returns('Close').iloc[-1]
        
        print(f"{year}:")
        print(f"  Trading Days: {stats['count']}")
        print(f"  Average: {stats['mean']:.2f}")
        print(f"  Range: {stats['min']:.2f} - {stats['max']:.2f}")
        print(f"  Total Return: {cum_return:.2f}%")
```

## Running Examples

To run the comprehensive example script:

```bash
conda activate mkt
cd /mnt/c/Users/ProsunHalder/Videos/MKT
python examples/stock_data_usage_examples.py
```

## API Reference

### StockDataReader Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `get_columns(columns)` | Get all or specific columns | DataFrame |
| `get_date_range(start, end, columns)` | Filter by date range | DataFrame |
| `get_from_date(from_date, columns)` | Get data from date onwards | DataFrame |
| `get_on_date(date, columns)` | Get data for specific date | Series |
| `get_lookback(from_date, days, columns)` | Get N days before date | DataFrame |
| `get_by_year(year, columns)` | Filter by year(s) | DataFrame |
| `get_by_quarter(year, quarter, columns)` | Filter by quarter(s) | DataFrame |
| `get_by_month(year, month, columns)` | Filter by month(s) | DataFrame |
| `get_by_week(year, week, columns)` | Filter by week(s) | DataFrame |
| `get_info()` | Get stock information | dict |

### StockDataAnalyzer Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `average(column)` | Calculate mean | float |
| `max_value(column)` | Get maximum with date | dict |
| `min_value(column)` | Get minimum with date | dict |
| `median(column)` | Calculate median | float |
| `std_dev(column)` | Standard deviation | float |
| `variance(column)` | Variance | float |
| `percentile(column, q)` | Calculate percentile | float |
| `summary_stats(column)` | Comprehensive statistics | dict |
| `simple_moving_average(column, window)` | SMA | Series |
| `exponential_moving_average(column, span)` | EMA | Series |
| `weighted_moving_average(column, window)` | WMA | Series |
| `cumulative_moving_average(column)` | CMA | Series |
| `returns(column, periods, percentage)` | Calculate returns | Series |
| `log_returns(column, periods)` | Logarithmic returns | Series |
| `cumulative_returns(column)` | Cumulative returns | Series |
| `volatility(column, window, annualize)` | Rolling volatility | Series |
| `daily_range()` | High - Low | Series |
| `average_true_range(window)` | ATR | Series |

## File Structure

```
MKT/
├── src/
│   └── data_fetch/
│       ├── stock_data_reader.py      # Data retrieval class
│       └── stock_data_analyzer.py    # Analysis class
├── examples/
│   └── stock_data_usage_examples.py  # Comprehensive examples
└── data/
    └── raw/
        └── *.csv                      # Stock CSV files
```

## Notes

- All operations are performed in the `mkt` conda environment
- Date formats should be 'YYYY-MM-DD' or datetime objects
- Missing dates will return the nearest available date with a warning
- All percentage values are returned as percentages (not decimals)
- Moving averages use `min_periods=1` to handle edge cases

## Error Handling

The system includes comprehensive error handling:

```python
try:
    reader = StockDataReader('invalid_file.csv')
except ValueError as e:
    print(f"Error: {e}")

try:
    data = reader.get_columns(['InvalidColumn'])
except ValueError as e:
    print(f"Error: {e}")
```

## Performance Tips

1. **Filter early**: Use date range filtering before analysis to reduce data size
2. **Reuse analyzers**: Create one analyzer and add multiple indicators
3. **Specific columns**: Request only needed columns to reduce memory usage

```python
# Good practice
data = reader.get_date_range('2024-01-01', '2024-12-31', 
                             columns=['Date', 'Close', 'Volume'])
analyzer = StockDataAnalyzer(data)
analyzer.simple_moving_average('Close', window=20, add_to_data=True)
analyzer.exponential_moving_average('Close', span=12, add_to_data=True)
results = analyzer.get_data()
```

## Contributing

Feel free to extend these classes with additional features:
- More technical indicators (RSI, MACD, Bollinger Bands)
- Pattern recognition
- Statistical tests
- Correlation analysis
