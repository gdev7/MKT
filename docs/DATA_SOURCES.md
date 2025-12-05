# Alternative Data Sources for Indian Stock Market

## Overview

While yfinance is convenient, there are multiple alternatives for fetching Indian stock market data, each with different advantages.

## 📊 Available Data Sources

### 1. **NSE India Official API** (Currently Used for Metadata)
**Pros:**
- Official source, most reliable
- Real-time data
- Free for personal use
- No rate limits (reasonable use)

**Cons:**
- Requires proper headers (anti-bot protection)
- No official documentation
- API endpoints can change
- No historical data older than 1 year directly

**Usage:**
```python
import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_nse_historical(symbol, from_date, to_date):
    """Fetch historical data from NSE."""
    url = f"https://www.nseindia.com/api/historical/cm/equity?symbol={symbol}&series=[%22EQ%22]&from={from_date}&to={to_date}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
    }
    
    session = requests.Session()
    # Get cookies first
    session.get("https://www.nseindia.com", headers=headers)
    
    response = session.get(url, headers=headers)
    data = response.json()
    
    df = pd.DataFrame(data['data'])
    return df

# Example
df = fetch_nse_historical('RELIANCE', '01-01-2024', '31-12-2024')
```

### 2. **NSEPython** (Wrapper Library)
**Pros:**
- Easy to use wrapper around NSE API
- Handles session management
- Multiple data types (indices, derivatives, etc.)
- Active maintenance

**Cons:**
- Third-party library
- May break if NSE changes API

**Installation:**
```bash
pip install nsepython
```

**Usage:**
```python
from nsepython import *

# Get historical data
df = equity_history(
    symbol="SBIN",
    series="EQ", 
    start_date="01-01-2024",
    end_date="31-12-2024"
)

# Get quote
quote = nse_quote_ltp("RELIANCE")

# Get option chain
chain = nse_optionchain_scrapper("NIFTY")
```

### 3. **BSE India API**
**Pros:**
- Official BSE source
- Alternative to NSE
- Good for stocks listed only on BSE

**Cons:**
- Less popular than NSE
- Limited historical data access
- Requires registration for some features

**Usage:**
```python
import requests

def fetch_bse_data(scrip_code):
    """Fetch BSE stock data."""
    url = f"https://api.bseindia.com/BseIndiaAPI/api/StockReachGraph/w?flag=0&fromdate=01/01/2024&todate=31/12/2024&seriesid=&scripcode={scrip_code}"
    
    response = requests.get(url)
    return response.json()

# Example: Reliance on BSE (scrip code: 500325)
data = fetch_bse_data("500325")
```

### 4. **Alpha Vantage** (Global Provider)
**Pros:**
- Professional API
- Good documentation
- Free tier available
- Supports NSE stocks

**Cons:**
- Rate limited (5 API calls/minute on free tier)
- Limited free data
- Requires API key

**Installation:**
```bash
pip install alpha-vantage
```

**Usage:**
```python
from alpha_vantage.timeseries import TimeSeries

ts = TimeSeries(key='YOUR_API_KEY', output_format='pandas')

# NSE stocks need .NSE suffix
data, meta_data = ts.get_daily(symbol='RELIANCE.NSE', outputsize='full')
```

### 5. **Quandl/Nasdaq Data Link**
**Pros:**
- High-quality curated data
- Multiple Indian data sources
- Historical data going back years
- RESTful API

**Cons:**
- Most Indian data requires paid subscription
- Limited free NSE/BSE data

**Installation:**
```bash
pip install quandl
```

**Usage:**
```python
import quandl

quandl.ApiConfig.api_key = 'YOUR_API_KEY'

# NSE data (requires subscription)
df = quandl.get('NSE/RELIANCE')
```

### 6. **Web Scraping from Financial Websites**
**Pros:**
- Free
- Multiple sources available
- Can get data yfinance might miss

**Cons:**
- Legally grey area
- Can break anytime
- Slower than APIs
- May violate terms of service

**Popular Sites:**
- moneycontrol.com
- investing.com
- screener.in
- economictimes.indiatimes.com

**Example (BeautifulSoup):**
```python
import requests
from bs4 import BeautifulSoup

def scrape_moneycontrol(symbol):
    # This is just an example - actual implementation depends on site structure
    url = f"https://www.moneycontrol.com/india/stockpricequote/{symbol}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Parse data...
    return data
```

### 7. **Upstox/Zerodha APIs** (Broker APIs)
**Pros:**
- Real-time tick data
- Very reliable
- Official broker APIs
- Good documentation

**Cons:**
- Requires trading account
- Monthly subscription (~₹2000/month)
- Primarily for live trading

**Zerodha Kite Connect:**
```python
from kiteconnect import KiteConnect

kite = KiteConnect(api_key="your_api_key")

# Historical data
data = kite.historical_data(
    instrument_token=408065,
    from_date="2024-01-01",
    to_date="2024-12-31",
    interval="day"
)
```

### 8. **Jugaad Data** (NSE/BSE Scraper)
**Pros:**
- Specifically built for Indian markets
- Free and open source
- Works with both NSE and BSE
- No API key needed

**Cons:**
- May break with website changes
- Slower than direct APIs

**Installation:**
```bash
pip install jugaad-data
```

**Usage:**
```python
from jugaad_data.nse import stock_df

# Fetch historical data
df = stock_df(
    symbol="SBIN",
    from_date=datetime(2024, 1, 1),
    to_date=datetime(2024, 12, 31),
    series="EQ"
)
```

### 9. **TrueData/Global Datafeeds** (Commercial)
**Pros:**
- Professional-grade data
- Very reliable
- Historical and real-time
- Tick-by-tick data available

**Cons:**
- Expensive (₹10,000+/month)
- Overkill for backtesting
- Requires subscription

### 10. **CSV Downloads from NSE/BSE**
**Pros:**
- Official source
- Free
- Complete historical data
- Bulk downloads available

**Cons:**
- Manual process
- Need to update regularly
- Not programmatic (unless automated with selenium)

**NSE Bulk Downloads:**
```
https://www.nseindia.com/market-data/live-equity-market
https://www.nseindia.com/all-reports
```

## 🔧 Recommended Approach for MKT Project

### **Option A: Multi-Source Fallback System**
```python
class DataFetcher:
    def fetch_stock_data(self, symbol, start_date, end_date):
        # Try sources in order of preference
        try:
            return self._fetch_from_nse(symbol, start_date, end_date)
        except Exception as e:
            logger.warning(f"NSE failed: {e}")
            
        try:
            return self._fetch_from_yfinance(symbol, start_date, end_date)
        except Exception as e:
            logger.warning(f"yfinance failed: {e}")
            
        try:
            return self._fetch_from_nsepython(symbol, start_date, end_date)
        except Exception as e:
            logger.error(f"All sources failed: {e}")
            raise DataFetchError("No data source available")
```

### **Option B: Primary + Backup**
- **Primary:** NSE Official API (for recent data, last 1 year)
- **Backup:** yfinance (for older historical data)
- **Validation:** Cross-check critical data between sources

### **Option C: Hybrid Approach (Recommended)**
```python
# For bulk historical download (one-time):
# 1. Download NSE bhav copies (daily files)
# 2. Process and store in local database

# For daily updates:
# 1. Use NSE API for today's data
# 2. Fallback to yfinance if NSE fails

# For missing data:
# 3. Use nsepython or jugaad-data
```

## 📝 Implementation Example for MKT

```python
# src/data_fetch/data_sources.py

class NSEDataSource:
    """Fetch data from NSE official API."""
    
    def fetch_historical(self, symbol, start_date, end_date):
        # Implementation here
        pass

class YFinanceDataSource:
    """Existing yfinance implementation."""
    
    def fetch_historical(self, symbol, start_date, end_date):
        # Current implementation
        pass

class JugaadDataSource:
    """Jugaad-data fallback."""
    
    def fetch_historical(self, symbol, start_date, end_date):
        from jugaad_data.nse import stock_df
        return stock_df(symbol, start_date, end_date, series="EQ")

# Multi-source fetcher
class MultiSourceFetcher:
    def __init__(self):
        self.sources = [
            NSEDataSource(),
            YFinanceDataSource(),
            JugaadDataSource()
        ]
    
    def fetch(self, symbol, start_date, end_date):
        for source in self.sources:
            try:
                data = source.fetch_historical(symbol, start_date, end_date)
                if data is not None and len(data) > 0:
                    logger.info(f"Data fetched from {source.__class__.__name__}")
                    return data
            except Exception as e:
                logger.warning(f"{source.__class__.__name__} failed: {e}")
                continue
        
        raise DataFetchError(f"Failed to fetch {symbol} from all sources")
```

## 🎯 Recommendation for Your Use Case

**Best Solution: NSEPython + yfinance fallback**

**Reasons:**
1. **NSEPython** is free, reliable, and specifically built for Indian markets
2. Handles NSE API complexities (sessions, cookies, headers)
3. **yfinance** as backup for when NSE API is down or rate-limited
4. Both are pip-installable and easy to maintain

**Implementation:**
```bash
# Add to requirements.txt
nsepython>=2.0.0
```

Then update `data_fetcher.py` to use NSEPython as primary and yfinance as fallback.

## 📊 Data Quality Comparison

| Source | Accuracy | Speed | Historical Depth | Reliability | Cost |
|--------|----------|-------|------------------|-------------|------|
| NSE Official | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ (1-2 years) | ⭐⭐⭐⭐ | Free |
| NSEPython | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | Free |
| yfinance | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ (10+ years) | ⭐⭐⭐ | Free |
| Jugaad Data | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Free |
| Alpha Vantage | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Free tier |
| Broker APIs | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ₹2000/mo |
| TrueData | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ₹10000+/mo |

## 🚀 Next Steps

1. **Try NSEPython** - Install and test with a few stocks
2. **Keep yfinance** - As proven backup
3. **Add validation** - Cross-check data between sources
4. **Monitor reliability** - Log which source is used for each fetch
5. **Consider caching** - Reduce API calls by caching daily data

Would you like me to implement a multi-source data fetcher with NSEPython as primary and yfinance as fallback?
