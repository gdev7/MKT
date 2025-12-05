# MKT Project Setup Guide

## Quick Start (Conda Environment)

### 1. Ensure you're in the conda environment
```bash
conda activate mkt
```

### 2. Install/Update Dependencies
```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install individually if needed:
pip install pandas>=2.0.0
pip install numpy>=1.24.0
pip install yfinance>=0.2.28
pip install requests>=2.31.0
pip install plotly>=5.17.0
pip install tqdm>=4.66.0
```

### 3. Verify Installation
```bash
python -c "import pandas; import numpy; import yfinance; print('All dependencies installed!')"
```

### 4. Test the System
```bash
# Sync metadata (already done)
python main.py --sync-metadata

# Test stock analysis
python main.py --analyze-stock RELIANCE --start-date 2024-01-01

# Test index analysis
python main.py --analyze-index "NIFTY 50" --top-n 5
```

## Using New Features

### Data Cleaning Example
```python
from src.preprocessing.data_cleaner import DataCleaner
from src.analysis.base_analyzer import BaseAnalyzer

# Load stock data
analyzer = BaseAnalyzer()
df = analyzer.load_stock_data('RELIANCE')

# Clean the data
cleaner = DataCleaner()
clean_df = cleaner.clean_stock_data(
    df,
    remove_outliers=True,
    handle_missing=True,
    validate_schema=True
)

print(f"Original: {len(df)} rows, Cleaned: {len(clean_df)} rows")
```

### Data Normalization Example
```python
from src.preprocessing.normalizer import DataNormalizer

normalizer = DataNormalizer()

# Normalize prices to 0-1 range
normalized_df = normalizer.normalize_prices(df, method='minmax')

# Resample to weekly data
weekly_df = normalizer.resample_ohlcv(df, timeframe='W')

# Calculate returns
returns_df = normalizer.calculate_returns(df, method='simple', periods=1)
```

### Backtesting Example
```python
from src.strategy.example_strategies import MovingAverageCrossoverStrategy
from src.strategy.backtester import Backtester
from src.analysis.base_analyzer import BaseAnalyzer

# Load data
analyzer = BaseAnalyzer()
data = analyzer.load_stock_data('RELIANCE')

# Create and initialize strategy
strategy = MovingAverageCrossoverStrategy()
strategy.initialize(fast_period=20, slow_period=50)

# Run backtest
backtester = Backtester(
    initial_capital=100000,
    commission=0.0005,  # 0.05%
    slippage=0.0001     # 0.01%
)

results = backtester.run(strategy, data, symbol='RELIANCE')

# Print results
backtester.print_results(results)
```

### Date Utilities Example
```python
from src.utils.date_utils import *
from datetime import date

# Check if today is a trading day
today = date.today()
if is_trading_day(today):
    print("Market is open today!")

# Get next trading day
next_day = get_next_trading_day(today)
print(f"Next trading day: {next_day}")

# Count trading days in a range
trading_days = count_trading_days('2025-01-01', '2025-12-31')
print(f"Trading days in 2025: {trading_days}")

# Get trading days between dates
days_list = get_trading_days_between('2025-01-01', '2025-01-31')
print(f"January 2025 has {len(days_list)} trading days")
```

### Custom Logging Example
```python
from src.utils.logger import get_logger

# Get a logger for your module
logger = get_logger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")

# Logs go to both console (INFO+) and file (ALL)
```

## Creating Your Own Strategy

### Step 1: Create Strategy Class
```python
from src.strategy.base_strategy import BaseStrategy, Signal
from src.utils.constants import TradeSide
import pandas as pd

class MyCustomStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(name="My Custom Strategy")
    
    def initialize(self, param1=10, param2=20, **kwargs):
        self.parameters = {
            'param1': param1,
            'param2': param2
        }
        self.logger.info(f"Initialized with params: {self.parameters}")
    
    def generate_signals(self, data: pd.DataFrame):
        self.validate_data(data)
        signals = []
        
        # Your signal generation logic here
        for i in range(len(data)):
            # Example: Buy on condition
            if some_condition:
                signal = Signal(
                    date=data.iloc[i]['DATE'],
                    symbol='STOCK',
                    side=TradeSide.BUY,
                    price=data.iloc[i]['CLOSE']
                )
                signals.append(signal)
        
        return signals
```

### Step 2: Backtest Your Strategy
```python
from src.strategy.backtester import Backtester

strategy = MyCustomStrategy()
strategy.initialize(param1=15, param2=25)

backtester = Backtester(initial_capital=100000)
results = backtester.run(strategy, data, symbol='SYMBOL')
backtester.print_results(results)
```

## Project Structure Overview

```
MKT/
├── requirements.txt          # Python dependencies
├── .gitignore               # Git exclusions
├── IMPROVEMENTS.md          # This improvements documentation
├── SETUP_GUIDE.md           # This file
├── main.py                  # Main CLI interface
├── src/
│   ├── config/
│   │   └── settings.py      # All configuration
│   ├── utils/               # Utility modules
│   │   ├── exceptions.py    # Custom exceptions
│   │   ├── logger.py        # Logging setup
│   │   ├── constants.py     # Constants & enums
│   │   └── date_utils.py    # Date/calendar helpers
│   ├── preprocessing/       # Data cleaning
│   │   ├── data_cleaner.py  # Cleaning operations
│   │   └── normalizer.py    # Normalization
│   ├── strategy/            # Trading strategies
│   │   ├── base_strategy.py       # Base class
│   │   ├── backtester.py          # Backtesting engine
│   │   ├── metrics.py             # Performance metrics
│   │   └── example_strategies.py  # Example strategies
│   ├── analysis/            # Existing analyzers
│   ├── data_fetch/          # Data fetching
│   ├── visualization/       # Charting
│   └── scripts/             # Utility scripts
```

## Configuration

All settings are in `src/config/settings.py`. Key configurations:

### API Settings
```python
API_RATE_LIMIT_DELAY = 1.0  # Seconds between requests
API_REQUEST_TIMEOUT = 10     # Request timeout
```

### Technical Indicators
```python
TECHNICAL_INDICATORS = {
    'SMA_PERIODS': [20, 50, 200],
    'EMA_PERIODS': [12, 26],
    'RSI_PERIOD': 14,
    # ... more
}
```

### Backtesting
```python
BACKTESTING_DEFAULTS = {
    'initial_capital': 100000,
    'commission': 0.0005,      # 0.05%
    'slippage': 0.0001,        # 0.01%
    'position_size': 0.1,      # 10% per position
}
```

## Troubleshooting

### Import Errors
If you see "Import could not be resolved":
```bash
conda activate mkt
pip install -r requirements.txt
```

### No Module Named 'src'
Make sure you're running from the project root:
```bash
cd /Users/halderp/Desktop/prosun/workspace/MKT
python main.py --help
```

### Type Checking Warnings
The type checking warnings from Pylance are normal - the code will run fine. They're due to dynamic pandas typing.

## Next Steps

1. ✅ Dependencies installed
2. ✅ Test basic commands
3. 📝 Create your own strategy
4. 📝 Run backtests
5. 📝 Analyze results
6. 📝 Optimize parameters
7. 📝 Paper trade (future)

## Resources

- **Command Reference:** See `COMMANDS.md`
- **Improvements:** See `IMPROVEMENTS.md`
- **Examples:** See `examples/` directory
- **Documentation:** See `docs/` directory

## Support

All code includes comprehensive docstrings. Use:
```python
help(ClassName)
help(function_name)
```

Or in IPython/Jupyter:
```python
ClassName?
function_name?
```

---
**Setup Guide Version:** 1.0  
**Date:** December 4, 2025  
**Conda Environment:** mkt
