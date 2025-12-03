# MKT - Stock Market Analysis Tool

A comprehensive Python-based stock market analysis framework for the Indian stock market (NSE).

## Features

### Three-Tier Analysis Framework

1. **Single Stock Analysis** - Deep technical analysis of individual stocks
   - Price statistics and trends
   - Volume analysis
   - Return calculations (1W, 1M, 3M, 1Y)
   - Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)

2. **Index/Group Analysis** - Comparative analysis of stocks within indices
   - Top gainers and losers
   - Volume leaders
   - Volatility analysis
   - Index-wide statistics

3. **Market-Wide Analysis** - Broad market statistics and trends
   - Market breadth (advance/decline ratio)
   - Top market performers
   - Sector performance comparison
   - Market volatility analysis

## Installation

```bash
# Activate the mkt conda environment
conda activate mkt

# Install dependencies (if needed)
pip install pandas numpy requests
```

## Usage

### Data Fetching

```bash
# Sync metadata with NSE
python main.py --sync-metadata

# Fetch historical data for a stock
python main.py --fetch-all RELIANCE

# Fetch latest data
python main.py --fetch-latest TCS
```

### Stock Analysis

```bash
# Analyze a single stock
python main.py --analyze-stock RELIANCE

# With date range
python main.py --analyze-stock RELIANCE --start-date 2024-01-01

# Analyze another stock
python main.py --analyze-stock TCS --start-date 2024-06-01
```

### Index Analysis

```bash
# List all available indices
python main.py --list-indices

# Analyze NIFTY 50
python main.py --analyze-index "NIFTY 50"

# With custom parameters
python main.py --analyze-index "NIFTY BANK" --start-date 2024-01-01 --top-n 5

# Analyze other indices
python main.py --analyze-index "NIFTY IT"
python main.py --analyze-index "NIFTY PHARMA"
```

### Market Analysis

```bash
# Full market analysis (may take time)
python main.py --analyze-market

# With date range and sample
python main.py --analyze-market --start-date 2024-11-01 --sample-size 100 --top-n 10

# Recent month analysis
python main.py --analyze-market --start-date 2024-11-01 --sample-size 200
```

## Command-Line Options

### Data Fetching
- `--fetch-all <SYMBOL>` - Fetch full history for a symbol
- `--fetch-latest <SYMBOL>` - Fetch latest data for a symbol
- `--fetch-today <SYMBOL>` - Fetch today's data for a symbol
- `--sync-metadata` - Sync metadata and raw data with NSE

### Analysis
- `--analyze-stock <SYMBOL>` - Analyze a single stock
- `--analyze-index <INDEX_NAME>` - Analyze stocks in an index
- `--analyze-market` - Analyze the entire market
- `--list-indices` - List all available indices

### Common Options
- `--start-date <YYYY-MM-DD>` - Start date for analysis
- `--end-date <YYYY-MM-DD>` - End date for analysis
- `--top-n <N>` - Number of top items to show (default: 10)
- `--sample-size <N>` - Sample size for market analysis

## Project Structure

```
MKT/
├── main.py                          # Main application entry point
├── src/
│   ├── analysis/                    # Analysis modules
│   │   ├── base_analyzer.py        # Base analyzer class
│   │   ├── stock_analyzer.py       # Single stock analysis
│   │   ├── index_analyzer.py       # Index/group analysis
│   │   └── dataset_analyzer.py     # Market-wide analysis
│   ├── config/                      # Configuration
│   │   └── settings.py             # Project settings
│   ├── data_fetch/                  # Data fetching modules
│   │   ├── data_fetcher.py         # Stock data fetcher
│   │   └── metadata_sync.py        # Metadata synchronization
│   ├── preprocessing/               # Data preprocessing
│   ├── utils/                       # Utility functions
│   └── visualization/               # Visualization tools
├── data/
│   ├── raw/                         # Raw stock data (CSV files)
│   ├── processed/                   # Processed data
│   └── metadata/                    # Stock metadata
│       ├── stocks_metadata.json    # Main metadata file
│       └── indices_config.json     # Index configuration
└── scripts/                         # Utility scripts
```

## Available Indices

The system tracks **113 unique indices** including:
- **Benchmark**: NIFTY 50, NIFTY 100, NIFTY 200, NIFTY 500
- **Sectoral**: NIFTY BANK, NIFTY IT, NIFTY PHARMA, NIFTY AUTO, NIFTY FMCG
- **Thematic**: NIFTY INDIA DEFENCE, NIFTY EV, NIFTY INDIA DIGITAL
- **Strategy**: NIFTY ALPHA 50, NIFTY LOW VOLATILITY 50, NIFTY DIVIDEND OPPORTUNITIES 50

Use `python main.py --list-indices` to see the complete list.

## Technical Indicators

### Single Stock Analysis Includes:
- **Moving Averages**: SMA (20, 50, 200), EMA (12, 26)
- **Momentum**: RSI (14-period)
- **Trend**: MACD (12, 26, 9)
- **Volatility**: Bollinger Bands (20-period, 2 std dev)

## Examples

### Example 1: Quick Stock Check
```bash
python main.py --analyze-stock INFY
```

### Example 2: Detailed Analysis with Date Range
```bash
python main.py --analyze-stock RELIANCE --start-date 2024-01-01 --end-date 2024-12-31
```

### Example 3: Compare Stocks in NIFTY 50
```bash
python main.py --analyze-index "NIFTY 50" --top-n 10
```

### Example 4: Market Snapshot
```bash
python main.py --analyze-market --start-date 2024-11-01 --sample-size 200 --top-n 15
```

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.