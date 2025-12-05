"""
Constants and enumerations for MKT application.
"""
from enum import Enum
from typing import Dict, List


class TimeFrame(Enum):
    """Time frame enumeration for analysis."""
    DAILY = "1d"
    WEEKLY = "1wk"
    MONTHLY = "1mo"
    QUARTERLY = "3mo"
    YEARLY = "1y"


class MarketStatus(Enum):
    """NSE market status enumeration."""
    PRE_OPEN = "pre_open"
    OPEN = "open"
    CLOSED = "closed"
    HOLIDAY = "holiday"


class TradeSide(Enum):
    """Trade side enumeration."""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order type enumeration."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LIMIT = "stop_limit"


class PositionType(Enum):
    """Position type enumeration."""
    LONG = "long"
    SHORT = "short"


# Column name constants
COLUMN_NAMES = {
    'DATE': 'DATE',
    'OPEN': 'OPEN',
    'HIGH': 'HIGH',
    'LOW': 'LOW',
    'CLOSE': 'CLOSE',
    'VOLUME': 'VOLUME',
    'PRICE': 'PRICE',  # Alias for CLOSE in some data sources
}

# Required columns for stock data
REQUIRED_COLUMNS = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']

# Index categories
INDEX_CATEGORIES = {
    'BENCHMARK': ['NIFTY 50', 'NIFTY 100', 'NIFTY 200', 'NIFTY 500'],
    'SECTORAL': [
        'NIFTY BANK', 'NIFTY IT', 'NIFTY PHARMA', 'NIFTY AUTO',
        'NIFTY FMCG', 'NIFTY METAL', 'NIFTY ENERGY', 'NIFTY REALTY',
        'NIFTY MEDIA', 'NIFTY PSU BANK'
    ],
    'THEMATIC': [
        'NIFTY INDIA DEFENCE', 'NIFTY EV', 'NIFTY INDIA DIGITAL',
        'NIFTY INFRASTRUCTURE', 'NIFTY COMMODITIES'
    ],
    'STRATEGY': [
        'NIFTY ALPHA 50', 'NIFTY LOW VOLATILITY 50',
        'NIFTY DIVIDEND OPPORTUNITIES 50', 'NIFTY QUALITY 30'
    ],
    'MARKET_CAP': [
        'NIFTY MIDCAP 100', 'NIFTY SMALLCAP 100',
        'NIFTY MIDCAP 50', 'NIFTY SMALLCAP 50'
    ]
}

# Technical indicator names
INDICATOR_NAMES = {
    'SMA': 'Simple Moving Average',
    'EMA': 'Exponential Moving Average',
    'RSI': 'Relative Strength Index',
    'MACD': 'Moving Average Convergence Divergence',
    'BB': 'Bollinger Bands',
    'ATR': 'Average True Range',
    'STOCH': 'Stochastic Oscillator',
    'ADX': 'Average Directional Index',
    'OBV': 'On-Balance Volume',
}

# Common stock symbols by sector
COMMON_SYMBOLS: Dict[str, List[str]] = {
    'BANKS': ['HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK'],
    'IT': ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM'],
    'AUTO': ['MARUTI', 'M&M', 'TATAMOTORS', 'BAJAJ-AUTO', 'HEROMOTOCO'],
    'PHARMA': ['SUNPHARMA', 'DRREDDY', 'CIPLA', 'DIVISLAB', 'LUPIN'],
    'ENERGY': ['RELIANCE', 'ONGC', 'BPCL', 'IOC', 'NTPC'],
    'FMCG': ['HINDUNILVR', 'ITC', 'NESTLEIND', 'BRITANNIA', 'DABUR'],
    'METALS': ['TATASTEEL', 'HINDALCO', 'JSWSTEEL', 'VEDL', 'COALINDIA'],
}

# Date format constants
DATE_FORMATS = {
    'INPUT': '%Y-%m-%d',
    'DISPLAY': '%d %b %Y',
    'FILE': '%Y%m%d',
    'DATETIME': '%Y-%m-%d %H:%M:%S',
}

# File extensions
FILE_EXTENSIONS = {
    'CSV': '.csv',
    'JSON': '.json',
    'HTML': '.html',
    'PNG': '.png',
    'PDF': '.pdf',
}

# Minimum data requirements
MIN_DATA_POINTS = {
    'ANALYSIS': 30,      # Minimum days for basic analysis
    'SMA_200': 200,      # For 200-day SMA
    'BACKTEST': 252,     # One year of data
    'OPTIMIZATION': 756  # Three years of data
}

# Risk-free rate (for Sharpe ratio calculation)
# Using approximate Indian government bond rate
RISK_FREE_RATE = 0.07  # 7% annual

# Ticker suffix for NSE symbols in yfinance
TICKER_SUFFIX = '.NS'

# Maximum allowed values (for validation)
MAX_VALUES = {
    'SAMPLE_SIZE': 5000,
    'TOP_N': 100,
    'YEARS_HISTORY': 25,
}
