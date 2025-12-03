# MKT Command Reference

Quick reference for all available commands in the MKT stock analysis tool.

## Prerequisites

```bash
# Activate conda environment
conda activate mkt
```

## Data Management Commands

### Sync Metadata
```bash
# Download and sync stock metadata from NSE
python main.py --sync-metadata
```

### Update Index Constituents
```bash
# Update all indices from config file
python src/scripts/update_indices.py --all

# Update a specific index
python src/scripts/update_indices.py --index "NIFTY 50" --url "https://..."

# Update NIFTY SMALLCAP 100 (shortcut)
python src/scripts/update_indices.py --smallcap
```

### Fetch Stock Data
```bash
# Fetch complete historical data for a stock
python main.py --fetch-all RELIANCE

# Fetch latest available data
python main.py --fetch-latest TCS

# Fetch today's data only
python main.py --fetch-today INFY

# Fetch by tag (if TAG field exists in metadata)
python main.py --tag <TAG_NAME>
```

## Analysis Commands

### 1. Single Stock Analysis

```bash
# Basic stock analysis
python main.py --analyze-stock RELIANCE

# With date range
python main.py --analyze-stock RELIANCE --start-date 2024-01-01

# With both start and end dates
python main.py --analyze-stock TCS --start-date 2024-01-01 --end-date 2024-12-31
```

**Output includes:**
- Price statistics (current, mean, min/max, 52-week high/low)
- Volume statistics
- Returns (1W, 1M, 3M, 1Y)
- Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)

### 2. Index/Group Analysis

```bash
# List all available indices
python main.py --list-indices

# Analyze an index
python main.py --analyze-index "NIFTY 50"

# With date range
python main.py --analyze-index "NIFTY BANK" --start-date 2024-01-01

# Show top 5 performers
python main.py --analyze-index "NIFTY IT" --top-n 5

# Complete example
python main.py --analyze-index "NIFTY PHARMA" --start-date 2024-01-01 --end-date 2024-12-31 --top-n 10
```

**Output includes:**
- Index statistics (avg return, volume)
- Top gainers and losers
- Volume leaders
- Most/least volatile stocks

**Popular Indices:**
- `"NIFTY 50"`, `"NIFTY 100"`, `"NIFTY 200"`, `"NIFTY 500"`
- `"NIFTY BANK"`, `"NIFTY IT"`, `"NIFTY PHARMA"`, `"NIFTY AUTO"`
- `"NIFTY FMCG"`, `"NIFTY METAL"`, `"NIFTY ENERGY"`
- `"NIFTY MIDCAP 100"`, `"NIFTY SMALLCAP 100"`

### 3. Market-Wide Analysis

```bash
# Analyze entire market (all stocks)
python main.py --analyze-market

# With sample size (recommended for speed)
python main.py --analyze-market --sample-size 100

# With date range
python main.py --analyze-market --start-date 2024-11-01

# Complete example
python main.py --analyze-market --start-date 2024-11-01 --sample-size 200 --top-n 15
```

**Output includes:**
- Market breadth (advance/decline ratio)
- Top market gainers and losers
- Volume leaders
- Top performing indices/sectors
- Market volatility analysis

## Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `--start-date` | Start date for analysis (YYYY-MM-DD) | `--start-date 2024-01-01` |
| `--end-date` | End date for analysis (YYYY-MM-DD) | `--end-date 2024-12-31` |
| `--top-n` | Number of top items to show | `--top-n 10` |
| `--sample-size` | Sample size for market analysis | `--sample-size 100` |

## Quick Examples

```bash
# Example 1: Quick stock check
python main.py --analyze-stock INFY

# Example 2: Detailed stock analysis
python main.py --analyze-stock RELIANCE --start-date 2024-01-01

# Example 3: Compare NIFTY 50 stocks
python main.py --analyze-index "NIFTY 50" --top-n 10

# Example 4: Banking sector analysis
python main.py --analyze-index "NIFTY BANK" --start-date 2024-06-01

# Example 5: Market snapshot (last month)
python main.py --analyze-market --start-date 2024-11-01 --sample-size 150

# Example 6: Full market analysis (may take time)
python main.py --analyze-market --top-n 20
```

## Help

```bash
# Show all available options
python main.py --help
```

## Tips

1. **Use date ranges** to focus on specific periods
2. **Use sampling** (`--sample-size`) for faster market analysis
3. **Adjust `--top-n`** to see more/fewer top performers
4. **List indices first** to find the exact index name
5. **Run in conda env `mkt`** for all dependencies

## Common Stock Symbols

- **Banks**: HDFCBANK, ICICIBANK, SBIN, KOTAKBANK, AXISBANK
- **IT**: TCS, INFY, WIPRO, HCLTECH, TECHM
- **Auto**: MARUTI, M&M, TATAMOTORS, BAJAJ-AUTO
- **Pharma**: SUNPHARMA, DRREDDY, CIPLA, DIVISLAB
- **Energy**: RELIANCE, ONGC, BPCL, IOC, NTPC
- **FMCG**: HINDUNILVR, ITC, NESTLEIND, BRITANNIA
