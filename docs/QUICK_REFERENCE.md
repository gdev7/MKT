# Stock Data Access System - Quick Reference

## Quick Start

```python
from src.data_fetch.stock_data_reader import StockDataReader
from src.data_fetch.stock_data_analyzer import StockDataAnalyzer

# Load data
reader = StockDataReader('data/raw/3MINDIA.csv')

# Get and analyze
data = reader.get_by_year(2024)
analyzer = StockDataAnalyzer(data)
```

## Common Use Cases

### 1. Get Recent Data (Last N Days)

```python
reader = StockDataReader('data/raw/RELIANCE.csv')
recent = reader.get_lookback('2024-12-01', days=30)
```

### 2. Year-over-Year Comparison

```python
for year in [2022, 2023, 2024]:
    data = reader.get_by_year(year)
    analyzer = StockDataAnalyzer(data)
    print(f"{year}: Avg = {analyzer.average('Close'):.2f}")
```

### 3. Calculate Moving Averages

```python
analyzer = StockDataAnalyzer(data)
sma_20 = analyzer.simple_moving_average('Close', 20, add_to_data=True)
sma_50 = analyzer.simple_moving_average('Close', 50, add_to_data=True)
result = analyzer.get_data()
```

### 4. Find Highs and Lows

```python
max_info = analyzer.max_value('Close')
min_info = analyzer.min_value('Close')
print(f"High: {max_info['value']} on {max_info['date']}")
print(f"Low: {min_info['value']} on {min_info['date']}")
```

### 5. Calculate Returns and Volatility

```python
daily_returns = analyzer.returns('Close', periods=1)
volatility = analyzer.volatility('Close', window=20)
cum_return = analyzer.cumulative_returns('Close').iloc[-1]
```

### 6. Quarter Analysis

```python
q1_data = reader.get_by_quarter(2024, 1)
q1_analyzer = StockDataAnalyzer(q1_data)
stats = q1_analyzer.summary_stats('Close')
```

### 7. Month-by-Month Breakdown

```python
for month in range(1, 13):
    month_data = reader.get_by_month(2024, month)
    if len(month_data) > 0:
        analyzer = StockDataAnalyzer(month_data)
        print(f"Month {month}: {analyzer.average('Close'):.2f}")
```

### 8. Date Range with Specific Columns

```python
data = reader.get_date_range(
    '2024-01-01', 
    '2024-12-31',
    columns=['Date', 'Close', 'Volume']
)
```

## All Available Methods

### StockDataReader

| Method | Example |
|--------|---------|
| `get_columns()` | `reader.get_columns(['Date', 'Close'])` |
| `get_date_range()` | `reader.get_date_range('2024-01-01', '2024-12-31')` |
| `get_from_date()` | `reader.get_from_date('2024-01-01')` |
| `get_on_date()` | `reader.get_on_date('2024-01-15')` |
| `get_lookback()` | `reader.get_lookback('2024-01-31', days=10)` |
| `get_by_year()` | `reader.get_by_year(2024)` or `reader.get_by_year([2023, 2024])` |
| `get_by_quarter()` | `reader.get_by_quarter(2024, 1)` |
| `get_by_month()` | `reader.get_by_month(2024, 1)` |
| `get_by_week()` | `reader.get_by_week(2024, 1)` |
| `get_info()` | `reader.get_info()` |

### StockDataAnalyzer

| Method | Example |
|--------|---------|
| `average()` | `analyzer.average('Close')` |
| `max_value()` | `analyzer.max_value('Close')` |
| `min_value()` | `analyzer.min_value('Close')` |
| `median()` | `analyzer.median('Close')` |
| `std_dev()` | `analyzer.std_dev('Close')` |
| `summary_stats()` | `analyzer.summary_stats('Close')` |
| `simple_moving_average()` | `analyzer.simple_moving_average('Close', 20)` |
| `exponential_moving_average()` | `analyzer.exponential_moving_average('Close', 12)` |
| `returns()` | `analyzer.returns('Close', periods=1)` |
| `volatility()` | `analyzer.volatility('Close', window=20)` |
| `daily_range()` | `analyzer.daily_range()` |
| `cumulative_returns()` | `analyzer.cumulative_returns('Close')` |

## Running Examples

```bash
conda activate mkt
cd /mnt/c/Users/ProsunHalder/Videos/MKT
python examples/stock_data_usage_examples.py
```

## Files Created

1. `/src/data_fetch/stock_data_reader.py` - Data retrieval class
2. `/src/data_fetch/stock_data_analyzer.py` - Analysis class
3. `/examples/stock_data_usage_examples.py` - Comprehensive examples
4. `/docs/STOCK_DATA_ACCESS_GUIDE.md` - Full documentation

## Available Columns

- `Date` - Trading date
- `Close` - Closing price
- `High` - Highest price
- `Low` - Lowest price
- `Open` - Opening price
- `Volume` - Trading volume
