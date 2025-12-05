import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Data directories
DATA_DIR = BASE_DIR / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
DATA_METADATA_DIR = DATA_DIR / "metadata"

# Metadata file
METADATA_FILE = DATA_METADATA_DIR / "stocks_metadata.json"
INDICES_CONFIG_FILE = DATA_METADATA_DIR / "indices_config.json"

# Output directories
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_CHARTS_DIR = OUTPUT_DIR / "charts"

# Ensure directories exist
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# API CONFIGURATION
# ============================================================================

# NSE API URLs
NSE_EQUITY_URL = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
NSE_INDEX_API_BASE = "https://www.nseindia.com/api/equity-stockIndices"

# API Request Settings
API_RATE_LIMIT_DELAY = 1.0  # Seconds between requests
API_REQUEST_TIMEOUT = 10    # Seconds

# NSE Headers (required for API access)
NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# ============================================================================
# DATA FETCHING DEFAULTS
# ============================================================================

DEFAULT_FETCH_YEARS = 20  # Number of years to fetch for historical data
DEFAULT_SAMPLE_SIZE = 100  # Default sample size for market analysis

# ============================================================================
# TECHNICAL INDICATORS CONFIGURATION
# ============================================================================

TECHNICAL_INDICATORS = {
    # Simple Moving Averages
    'SMA_PERIODS': [20, 50, 200],
    
    # Exponential Moving Averages
    'EMA_PERIODS': [12, 26],
    
    # Relative Strength Index
    'RSI_PERIOD': 14,
    
    # MACD (Moving Average Convergence Divergence)
    'MACD_FAST': 12,
    'MACD_SLOW': 26,
    'MACD_SIGNAL': 9,
    
    # Bollinger Bands
    'BB_PERIOD': 20,
    'BB_STD_DEV': 2,
    
    # Average True Range
    'ATR_PERIOD': 14,
    
    # Volume Moving Average
    'VOLUME_MA_PERIOD': 20
}

# ============================================================================
# ANALYSIS DEFAULTS
# ============================================================================

DEFAULT_TOP_N = 10  # Default number of top items to show in rankings

# Return calculation periods (in trading days)
RETURN_PERIODS = {
    '1W': 5,    # 1 week
    '1M': 21,   # 1 month
    '3M': 63,   # 3 months
    '6M': 126,  # 6 months
    '1Y': 252   # 1 year
}

# ============================================================================
# VISUALIZATION CONFIGURATION
# ============================================================================

# Default chart dimensions
CHART_HEIGHT = 800
CHART_WIDTH = 1400

# Color schemes for candlestick charts
COLOR_SCHEMES = {
    'default': {
        'increasing': '#26a69a',  # Teal green
        'decreasing': '#ef5350'   # Red
    },
    'classic': {
        'increasing': '#00ff00',  # Bright green
        'decreasing': '#ff0000'   # Bright red
    },
    'dark': {
        'increasing': '#00c853',  # Material green
        'decreasing': '#d50000'   # Material red
    }
}

# Moving average colors (for up to 5 MAs)
MA_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

# Volume bar colors
VOLUME_COLORS = {
    'increasing': 'rgba(38, 166, 154, 0.5)',
    'decreasing': 'rgba(239, 83, 80, 0.5)'
}

# ============================================================================
# TRADING CALENDAR CONFIGURATION
# ============================================================================

# NSE Trading Hours (IST)
TRADING_HOURS = {
    'pre_open_start': '09:00',
    'pre_open_end': '09:15',
    'market_open': '09:15',
    'market_close': '15:30',
    'post_close_start': '15:40',
    'post_close_end': '16:00'
}

# Weekend days (NSE is closed)
WEEKEND_DAYS = [5, 6]  # Saturday, Sunday (0=Monday, 6=Sunday)

# NSE Public Holidays 2025 (will need annual updates)
NSE_HOLIDAYS_2025 = [
    '2025-01-26',  # Republic Day
    '2025-03-14',  # Holi
    '2025-03-31',  # Id-Ul-Fitr
    '2025-04-10',  # Mahavir Jayanti
    '2025-04-14',  # Dr. Ambedkar Jayanti
    '2025-04-18',  # Good Friday
    '2025-05-01',  # Maharashtra Day
    '2025-06-07',  # Id-Ul-Adha
    '2025-08-15',  # Independence Day
    '2025-08-27',  # Ganesh Chaturthi
    '2025-10-02',  # Gandhi Jayanti
    '2025-10-20',  # Dussehra
    '2025-11-01',  # Diwali (Laxmi Pujan)
    '2025-11-05',  # Gurunanak Jayanti
    '2025-12-25',  # Christmas
]

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FILE = BASE_DIR / 'mkt.log'

# ============================================================================
# PERFORMANCE & OPTIMIZATION
# ============================================================================

# Enable caching for expensive operations
ENABLE_CACHE = True
CACHE_DIR = BASE_DIR / '.cache'

# Parallel processing settings
MAX_WORKERS = 4  # Number of parallel workers for multi-stock operations

# ============================================================================
# BACKTESTING CONFIGURATION
# ============================================================================

# Default backtesting settings
BACKTESTING_DEFAULTS = {
    'initial_capital': 100000,      # Starting capital in INR
    'commission': 0.0005,           # 0.05% per trade
    'slippage': 0.0001,             # 0.01% slippage
    'position_size': 0.1,           # 10% of portfolio per position
    'max_positions': 10,            # Maximum concurrent positions
    'risk_per_trade': 0.02,         # 2% risk per trade
}

# Performance metrics to calculate
PERFORMANCE_METRICS = [
    'total_return',
    'annual_return',
    'sharpe_ratio',
    'sortino_ratio',
    'max_drawdown',
    'win_rate',
    'profit_factor',
    'total_trades',
    'avg_trade_return',
]

