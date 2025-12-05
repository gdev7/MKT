# Multi-Source Data Fetcher

The MKT project now includes a robust multi-source data fetcher that automatically falls back to alternative sources if the primary source fails.

## Overview

The multi-source fetcher tries multiple data sources in priority order:

1. **NSEPython** (Primary) - Direct NSE data, free and reliable
2. **NSE Official API** (Secondary) - Official NSE API
3. **YFinance** (Fallback) - Reliable international source

## Architecture

### Components

```
src/data_fetch/
├── data_source.py              # Abstract base class
├── nsepython_source.py         # NSEPython implementation
├── nse_official_source.py      # NSE Official API implementation
├── yfinance_source.py          # YFinance implementation
├── multi_source_fetcher.py     # Orchestrator with fallback logic
└── data_fetcher.py             # Updated main fetcher class
```

## Usage

### Basic Usage (Automatic Multi-Source)

```python
from src.data_fetch.data_fetcher import DataFetcher

# Initialize with multi-source enabled (default)
fetcher = DataFetcher(use_multi_source=True)

# Fetch data - automatically tries multiple sources
data = fetcher.fetch_all("RELIANCE", years=5)
```

### Direct Multi-Source Fetcher

```python
from src.data_fetch.multi_source_fetcher import MultiSourceFetcher
from datetime import datetime, timedelta

# Initialize
fetcher = MultiSourceFetcher()

# Fetch data
end_date = datetime.now().date()
start_date = end_date - timedelta(days=365)

data = fetcher.fetch("TCS", start_date, end_date)

# Check which source was used
if data is not None:
    source = data['Source'].iloc[0]
    print(f"Data fetched from: {source}")
```

### Preferred Source

```python
# Prefer a specific source
data = fetcher.fetch("INFY", start_date, end_date, preferred_source="YFinance")
```

### Legacy Mode (YFinance Only)

```python
# Use yfinance only (old behavior)
fetcher = DataFetcher(use_multi_source=False)
data = fetcher.fetch_all("HDFCBANK", years=10)
```

## Features

### Automatic Fallback

The fetcher automatically tries sources in order until data is retrieved:

```
NSEPython fails → Try NSE Official → Try YFinance → Raise error
```

### Data Validation

Each source validates data before returning:
- Checks for required columns (Date, Open, High, Low, Close, Volume)
- Ensures non-empty data
- Standardizes column names

### Source Tracking

All fetched data includes a `Source` column indicating which source provided the data:

```python
print(data['Source'].unique())
# Output: ['NSEPython'] or ['YFinance']
```

### Logging

Comprehensive logging at each step:

```
INFO: Available sources: ['NSEPython', 'NSE Official', 'YFinance']
DEBUG: Trying NSEPython for RELIANCE
INFO: Successfully fetched RELIANCE from NSEPython (250 records)
```

## Installation

### Install Required Packages

```bash
# Activate conda environment
conda activate mkt

# Install dependencies
pip install nsepython>=2.4
pip install yfinance>=0.2.28
pip install requests>=2.31.0
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

## Testing

### Run Test Script

```bash
python tests/test_multi_source.py
```

This will:
1. Check which sources are available
2. Test fetching data from multiple symbols
3. Display results and source used for each symbol

### Expected Output

```
==========================================================
SOURCE AVAILABILITY TEST
==========================================================

NSEPython            - ✓ Available
NSE Official         - ✓ Available
YFinance             - ✓ Available

==========================================================
MULTI-SOURCE DATA FETCHER TEST
==========================================================

Available sources: ['NSEPython', 'NSE Official', 'YFinance']

Fetching data from 2024-12-20 to 2025-01-19

==========================================================
Testing: RELIANCE
==========================================================
✓ Success!
  Records: 21
  Source: NSEPython
  Date range: 2024-12-20 to 2025-01-17
```

## Advanced Usage

### Custom Source Priority

```python
from src.data_fetch.multi_source_fetcher import MultiSourceFetcher
from src.data_fetch.yfinance_source import YFinanceSource
from src.data_fetch.nsepython_source import NSEPythonSource

# Create custom priority order (YFinance first)
sources = [
    YFinanceSource(),
    NSEPythonSource(),
]

fetcher = MultiSourceFetcher(sources=sources)
```

### Check Available Sources

```python
fetcher = MultiSourceFetcher()

# Get list of available sources
available = fetcher.get_available_sources()
print(f"Available: {available}")

# Get specific source
nse_source = fetcher.get_source_by_name("NSEPython")
```

### Error Handling

```python
from src.utils.exceptions import DataFetchError

try:
    data = fetcher.fetch("INVALID_SYMBOL", start_date, end_date)
except DataFetchError as e:
    print(f"Failed to fetch data: {e}")
```

## Data Source Details

### NSEPython

- **Type**: Python library wrapping NSE API
- **Pros**: Direct NSE data, free, comprehensive
- **Cons**: May have rate limits, requires internet
- **Installation**: `pip install nsepython`

### NSE Official API

- **Type**: Direct NSE REST API
- **Pros**: Official source, real-time
- **Cons**: Rate limiting, session management, limited history
- **Installation**: Built-in (uses requests)

### YFinance

- **Type**: Yahoo Finance API wrapper
- **Pros**: Very reliable, extensive history
- **Cons**: Third-party source, occasional data gaps
- **Installation**: `pip install yfinance`

## Configuration

### Settings

Edit `src/config/settings.py`:

```python
# API settings
API_REQUEST_TIMEOUT = 30  # seconds
API_RATE_LIMIT_DELAY = 1.0  # seconds between requests

# NSE headers for official API
NSE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 ...',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
}
```

## Troubleshooting

### NSEPython not working

```bash
# Check installation
pip list | grep nsepython

# Reinstall
pip install --upgrade nsepython
```

### All sources failing

1. Check internet connection
2. Verify symbol is valid (check `data/metadata/EQUITY_L.csv`)
3. Check logs in `logs/mkt.log`
4. Try specific source:

```python
# Test specific source
from src.data_fetch.yfinance_source import YFinanceSource

source = YFinanceSource()
if source.is_available():
    data = source.fetch_historical("RELIANCE", start_date, end_date)
```

### Rate limiting issues

Increase delay between requests:

```python
fetcher = DataFetcher(delay=2.0)  # 2 seconds between calls
```

## Best Practices

1. **Use multi-source by default** - More reliable than single source
2. **Monitor logs** - Check which sources are being used
3. **Validate symbols** - Check metadata before fetching
4. **Handle errors gracefully** - Always catch DataFetchError
5. **Respect rate limits** - Use appropriate delays

## Migration from Legacy

If you have existing code using old DataFetcher:

```python
# Old code (still works)
fetcher = DataFetcher()
data = fetcher.fetch_all("RELIANCE")

# New code (recommended)
fetcher = DataFetcher(use_multi_source=True)
data = fetcher.fetch_all("RELIANCE")
```

No changes needed - multi-source is backward compatible!

## Future Enhancements

Potential additions:
- Alpha Vantage source
- Broker API sources
- CSV file source
- Database caching
- Parallel source queries
- Custom source plugins
