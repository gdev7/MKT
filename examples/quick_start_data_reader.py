#!/usr/bin/env python3
"""
Quick Start: Using DataReader

This script shows the most common DataReader use cases.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.data_reader import DataReader
from src.analysis.trend_detector import TrendFilter, TrendType

# ============================================================
# BASIC USAGE
# ============================================================

reader = DataReader()

# Get price data
df = reader.get_price_data('HDFCBANK')
print(f"Loaded {len(df)} days of HDFCBANK data")

# Get latest price
price = reader.get_latest_price('RELIANCE')
print(f"RELIANCE: ₹{price:.2f}")

# Get metadata
metadata = reader.get_stock_metadata('TCS')
print(f"TCS Market Cap: {metadata.get('MARKET_CAP')} Cr")

# ============================================================
# FILTERING
# ============================================================

# By index
nifty50 = reader.get_stocks_by_index('NIFTY 50')
print(f"\nNIFTY 50: {len(nifty50)} stocks")

# By market cap
large_caps = reader.get_stocks_by_market_cap(min_cap=50000)
print(f"Large caps (>50k Cr): {len(large_caps)} stocks")

# By sector
it_stocks = reader.get_stocks_by_sector('IT', level='SECTOR_GROUP')
print(f"IT sector: {len(it_stocks)} stocks")

# Combined filters
large_cap_nifty50 = set(nifty50) & set(large_caps)
print(f"Large cap NIFTY 50: {len(large_cap_nifty50)} stocks")

# ============================================================
# TREND FILTERING
# ============================================================

trend_filter = TrendFilter(data_reader=reader)

# Find uptrend stocks
uptrend = trend_filter.filter_by_trend(
    symbols=nifty50,
    trend_type=TrendType.UPTREND,
    period=20,
    min_strength=0.6
)
print(f"\nUptrend stocks: {len(uptrend)}")

# ============================================================
# BATCH OPERATIONS
# ============================================================

# Load multiple stocks efficiently
symbols = ['RELIANCE', 'TCS', 'HDFCBANK']
data = reader.get_multiple_stocks(symbols, include_prices=True, days=30)

for symbol, stock_data in data.items():
    stats = stock_data['price_stats']
    if stats:
        print(f"{symbol}: ₹{stats['current']:.2f} ({stats['change_pct']:+.2f}%)")

# ============================================================
# SEARCH
# ============================================================

# Search for stocks
hdfc_stocks = reader.search_stocks('HDFC')
print(f"\nHDFC stocks: {hdfc_stocks}")

# ============================================================
# COMPLETE WORKFLOW EXAMPLE
# ============================================================

print("\n" + "="*60)
print("COMPLETE WORKFLOW: Find strong uptrend large caps")
print("="*60)

# Step 1: Get NIFTY 50 stocks
universe = reader.get_stocks_by_index('NIFTY 50')

# Step 2: Filter large caps
large_caps = [s for s in universe 
              if s in reader.get_stocks_by_market_cap(min_cap=50000)]

# Step 3: Find uptrend stocks
uptrend_stocks = trend_filter.filter_by_trend(
    symbols=large_caps,
    trend_type=TrendType.UPTREND,
    min_strength=0.6
)

# Step 4: Get complete data
print(f"\nFound {len(uptrend_stocks)} stocks:")
for symbol in uptrend_stocks[:5]:  # Top 5
    complete = reader.get_stock_complete(symbol, days=30)
    metadata = complete['metadata']
    stats = complete['price_stats']
    
    print(f"\n{symbol} - {metadata.get('NAME OF COMPANY')}")
    print(f"  Market Cap: ₹{metadata.get('MARKET_CAP')} Cr")
    print(f"  Current: ₹{stats['current']:.2f}")
    print(f"  30-day change: {stats['change_pct']:+.2f}%")
