# Data Reader Guide

Complete guide for using the `DataReader` class - unified data access layer.

## Overview

`DataReader` provides a clean, unified interface to all stock market data:
- **Price data (OHLCV)**: Historical daily prices from CSV files
- **Enriched metadata**: Financial ratios, shareholding patterns, sectors
- **Index memberships**: NIFTY 50, SMALLCAP 100, sectoral indices
- **Data filtering**: By sector, market cap, index, or custom criteria

## Quick Start

```python
from src.utils.data_reader import DataReader

reader = DataReader()

# Load price data
df = reader.get_price_data('HDFCBANK')

# Get metadata
metadata = reader.get_stock_metadata('HDFCBANK')

# Filter by index
nifty50 = reader.get_stocks_by_index('NIFTY 50')
```

## Features

### 1. Price Data Loading

```python
# Full historical data
df = reader.get_price_data('RELIANCE')
# Returns DataFrame with columns: date, open, high, low, close, volume

# Date range filtering
df = reader.get_price_data('TCS', 
                           start_date='2024-01-01',
                           end_date='2024-12-31')

# Latest price
price = reader.get_latest_price('INFY')  # Returns float

# Price statistics
stats = reader.get_price_range('HDFCBANK', days=30)
# Returns: {high, low, avg, current, change_pct, days}
```

### 2. Metadata Access

```python
# Single stock metadata
metadata = reader.get_stock_metadata('SBIN')
# Returns: Dict with MARKET_CAP, PE_RATIO, ROE, SECTOR, etc.

# All metadata
all_stocks = reader.get_all_metadata()
# Returns: Dict[symbol -> metadata]

# Complete stock data (metadata + price)
data = reader.get_stock_complete('ICICIBANK', days=90)
# Returns: {symbol, metadata, price_data, price_stats}
```

### 3. Filter by Index

```python
# NIFTY 50 stocks
nifty50 = reader.get_stocks_by_index('NIFTY 50')

# NIFTY SMALLCAP 100
smallcap = reader.get_stocks_by_index('NIFTY SMALLCAP 100')

# NIFTY BANK
banks = reader.get_stocks_by_index('NIFTY BANK')

# NIFTY AUTO
auto = reader.get_stocks_by_index('NIFTY AUTO')
```

### 4. Filter by Sector

```python
# IT sector stocks
it_stocks = reader.get_stocks_by_sector('IT', level='SECTOR_GROUP')

# Pharma stocks
pharma = reader.get_stocks_by_sector('Pharma', level='SECTOR_GROUP')

# Banking sector
banking = reader.get_stocks_by_sector('Banking', level='SECTOR_GROUP')

# Sector levels: BROAD_SECTOR, SECTOR_GROUP, SECTOR, SUB_SECTOR
```

### 5. Filter by Market Cap

```python
# Large caps (> 1 lakh crore)
large_caps = reader.get_stocks_by_market_cap(min_cap=100000)

# Mid caps (10k - 1 lakh crore)
mid_caps = reader.get_stocks_by_market_cap(min_cap=10000, max_cap=100000)

# Small caps (< 10k crore)
small_caps = reader.get_stocks_by_market_cap(max_cap=10000)

# Custom range
custom = reader.get_stocks_by_market_cap(min_cap=50000, max_cap=200000)
```

### 6. Combined Filters

```python
# Large-cap IT stocks in NIFTY 50
nifty50 = set(reader.get_stocks_by_index('NIFTY 50'))
it_stocks = set(reader.get_stocks_by_sector('IT', level='SECTOR_GROUP'))
large_caps = set(reader.get_stocks_by_market_cap(min_cap=50000))

result = nifty50 & it_stocks & large_caps

# Mid-cap pharma stocks
pharma = set(reader.get_stocks_by_sector('Pharma', level='SECTOR_GROUP'))
mid_caps = set(reader.get_stocks_by_market_cap(min_cap=10000, max_cap=100000))

result = pharma & mid_caps
```

### 7. Search Stocks

```python
# Search by symbol
results = reader.search_stocks('HDFC')
# Returns: ['HDFCAMC', 'HDFCBANK', 'HDFCLIFE']

# Search by company name
results = reader.search_stocks('BANK')
# Returns: All stocks with 'BANK' in symbol or name

# Search with custom fields
results = reader.search_stocks('Technology', 
                               search_fields=['SECTOR', 'SUB_SECTOR'])
```

### 8. Batch Operations

```python
# Load multiple stocks efficiently
symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK']

# Metadata only
data = reader.get_multiple_stocks(symbols, include_prices=False)

# With price data
data = reader.get_multiple_stocks(symbols, 
                                  include_prices=True, 
                                  days=30)

# Returns: Dict[symbol -> {metadata, price_data, price_stats}]
```

### 9. Utility Methods

```python
# Available symbols with price data
symbols = reader.get_available_symbols()

# Symbols with enriched metadata
enriched = reader.get_enriched_symbols()

# Symbol information
info = reader.get_symbol_info('HDFCBANK')
# Returns: {has_price_data, has_metadata, has_enrichment, metadata}

# Summary statistics
stats = reader.get_summary_stats()
# Returns: {total_stocks_in_metadata, stocks_with_price_data, 
#           enriched_stocks, available_indices, index_count}
```

## Integration with Trend Detection

Combine `DataReader` with `TrendFilter` for powerful stock screening:

```python
from src.utils.data_reader import DataReader
from src.analysis.trend_detector import TrendFilter, TrendType

reader = DataReader()
trend_filter = TrendFilter()

# Get NIFTY 50 stocks
nifty50 = reader.get_stocks_by_index('NIFTY 50')

# Filter for uptrend stocks
uptrend_stocks = trend_filter.filter_by_trend(
    symbols=nifty50,
    trend_type=TrendType.UPTREND,
    period=20,
    min_strength=0.7
)

# Get large-cap uptrend stocks
large_caps = set(reader.get_stocks_by_market_cap(min_cap=50000))
uptrend_large_caps = [s for s in uptrend_stocks if s in large_caps]

# Get enriched metadata for final stocks
for symbol in uptrend_large_caps:
    metadata = reader.get_stock_metadata(symbol)
    stats = reader.get_price_range(symbol, days=30)
    
    print(f"{symbol}:")
    print(f"  Market Cap: {metadata.get('MARKET_CAP')} Cr")
    print(f"  PE: {metadata.get('PE_RATIO')}")
    print(f"  30-day change: {stats['change_pct']:+.2f}%")
```

## Performance Features

### Caching

Metadata is cached for 5 minutes to reduce file I/O:

```python
# First call loads from file
metadata = reader.get_all_metadata()

# Subsequent calls use cache (within 5 minutes)
metadata = reader.get_all_metadata()

# Force reload
metadata = reader.get_all_metadata(force_reload=True)
```

### Efficient Batch Loading

Use `get_multiple_stocks()` instead of loops:

```python
# ❌ Inefficient
data = {}
for symbol in symbols:
    data[symbol] = reader.get_stock_complete(symbol)

# ✅ Efficient
data = reader.get_multiple_stocks(symbols, include_prices=True)
```

## Configuration

Customize data paths:

```python
reader = DataReader(
    data_dir="data",
    raw_dir="data/raw",
    metadata_file="data/metadata/stocks_metadata.json",
    indices_config="data/metadata/indices_config.json"
)
```

## Complete Example

```python
from src.utils.data_reader import DataReader
from src.analysis.trend_detector import TrendFilter, TrendType

# Initialize
reader = DataReader()
trend_filter = TrendFilter()

print("Stock Screening Pipeline")
print("="*70)

# Step 1: Get universe (NIFTY SMALLCAP 100)
universe = reader.get_stocks_by_index('NIFTY SMALLCAP 100')
print(f"Universe: {len(universe)} stocks")

# Step 2: Filter by market cap (> 5000 Cr)
min_cap_stocks = [s for s in universe 
                  if s in reader.get_stocks_by_market_cap(min_cap=5000)]
print(f"Market cap filter: {len(min_cap_stocks)} stocks")

# Step 3: Filter by trend (uptrend)
uptrend_stocks = trend_filter.filter_by_trend(
    symbols=min_cap_stocks,
    trend_type=TrendType.UPTREND,
    min_strength=0.6
)
print(f"Uptrend filter: {len(uptrend_stocks)} stocks")

# Step 4: Get complete data for final stocks
print(f"\nFinal Stocks:")
print("-"*70)

for symbol in uptrend_stocks:
    data = reader.get_stock_complete(symbol, days=30)
    
    metadata = data['metadata']
    stats = data['price_stats']
    
    print(f"\n{symbol} - {metadata.get('NAME OF COMPANY')}")
    print(f"  Sector: {metadata.get('SECTOR')}")
    print(f"  Market Cap: ₹{metadata.get('MARKET_CAP')} Cr")
    print(f"  Current Price: ₹{stats['current']:.2f}")
    print(f"  30-day Change: {stats['change_pct']:+.2f}%")
```

## API Reference

### Class: DataReader

#### Constructor
- `__init__(data_dir, raw_dir, metadata_file, indices_config)`

#### Price Data
- `get_price_data(symbol, start_date, end_date)` → DataFrame
- `get_latest_price(symbol)` → float
- `get_price_range(symbol, days)` → Dict

#### Metadata
- `get_all_metadata(force_reload)` → Dict
- `get_stock_metadata(symbol, force_reload)` → Dict
- `get_stocks_by_field(field, value)` → List[str]
- `get_stocks_by_index(index_name)` → List[str]
- `get_stocks_by_sector(sector, level)` → List[str]
- `get_stocks_by_market_cap(min_cap, max_cap)` → List[str]

#### Combined
- `get_stock_complete(symbol, days)` → Dict
- `get_multiple_stocks(symbols, include_prices, days)` → Dict

#### Utilities
- `get_available_symbols()` → List[str]
- `get_enriched_symbols()` → List[str]
- `get_symbol_info(symbol)` → Dict
- `search_stocks(query, search_fields)` → List[str]
- `get_summary_stats()` → Dict

## Examples

See `examples/data_reader_examples.py` for 10 complete examples:
1. Basic data loading
2. Price analysis
3. Filter by index
4. Filter by sector
5. Filter by market cap
6. Combined filters
7. Complete stock data
8. Search stocks
9. Multiple stocks
10. Summary statistics

Run examples:
```bash
python examples/data_reader_examples.py
```

## Notes

- CSV files must be in `data/raw/` directory
- Metadata must be in `data/metadata/stocks_metadata.json`
- Price data format: skiprows=2, columns=['date', 'close', 'high', 'low', 'open', 'volume']
- Metadata is cached for 5 minutes
- All prices are in INR (₹)
- Market cap values are in Crores (Cr)
