# MKT - Indian Stock Market Analysis & Data Enrichment

A comprehensive Python framework for analyzing Indian stocks with automated data enrichment from Screener.in.

## 🚀 Features

### Stock Data Enrichment
- **Automated metadata enrichment** from Screener.in
- **4-level sector hierarchy** (Broad Sector → Sector Group → Sector → Sub-Sector)
- **Comprehensive financial ratios** (Market Cap, P/E, ROE, ROCE, Dividend Yield, etc.)
- **Shareholding patterns** (quarterly data for Promoters, FIIs, DIIs, Public)
- **Quarterly results** (13 quarters of financial data)
- **Growth metrics** (Sales/Profit growth 3Y, 5Y, TTM)

### Technical Analysis
- Price statistics and trends
- Volume analysis
- Return calculations (1W, 1M, 3M, 1Y)
- Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)

### Index & Portfolio Analysis
- Index-based filtering and analysis
- Market cap range filtering
- Sector-wise analysis
- Top gainers/losers identification

## 📦 Installation

```bash
# Activate the mkt conda environment
conda activate mkt

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Quick Start

### 1. Enrich Stock Metadata

```bash
# Enrich all NIFTY 50 stocks
python src/scripts/enrich_stocks.py --index "NIFTY 50"

# Enrich stocks by market cap range (1000-10000 Cr)
python src/scripts/enrich_stocks.py --market-cap-min 1000 --market-cap-max 10000

# Enrich only unenriched stocks
python src/scripts/enrich_stocks.py --filter-enriched

# Test mode (5 stocks only)
python src/scripts/enrich_stocks.py --test
```

### 2. View Enriched Data

```bash
# View shareholding pattern
python src/scripts/view_shareholding.py RELIANCE

# View historical changes
python src/scripts/view_history.py TCS

# View time-series data (quarterly results)
python src/scripts/view_timeseries.py HDFCBANK
```

### 3. Update Stock Indices

```bash
# Update index memberships (NIFTY 50, NIFTY 100, etc.)
python src/scripts/update_indices.py

# Check which indices a stock belongs to
python src/scripts/check_indices.py INFY
```

### 4. Fetch Price Data

```bash
# Fetch all historical data for a stock
python main.py --fetch-all RELIANCE

# Fetch only latest data
python main.py --fetch-latest TCS

# Sync metadata from NSE
python main.py --sync-metadata
```

## 📊 Data Structure

The enriched `data/metadata/stocks_metadata.json` contains:

```json
{
  "RELIANCE": {
    "SYMBOL": "RELIANCE",
    "NAME OF COMPANY": "Reliance Industries Limited",
    
    "MARKET_CAP": "1850000",
    "CURRENT_PRICE": "2745",
    "PE_RATIO": "28.5",
    "ROE": "12.5",
    "ROCE": "15.2",
    
    "BROAD_SECTOR": "Energy",
    "SECTOR_GROUP": "Oil Gas & Consumable Fuels",
    "SECTOR": "Refineries & Marketing",
    "SUB_SECTOR": "Petroleum Products",
    
    "SHAREHOLDING_PATTERN": [
      {"quarter": "Sep 2025", "type": "Promoters", "percentage": "50.39%"},
      ...
    ],
    
    "QUARTERLY_RESULTS": [
      {"quarter": "Sep 2025", "sales": "245000", "operating_profit": "42000", ...},
      ...
    ],
    
    "HISTORY": {
      "MARKET_CAP": {"value": "1850000", "changed": "2025-12-05"},
      ...
    }
  }
}
```

## 🛠️ Project Structure

```
MKT/
├── data/
│   ├── metadata/
│   │   └── stocks_metadata.json         # Enriched stock metadata
│   ├── raw/                              # Historical price data (CSV)
│   └── processed/                        # Processed datasets
│
├── src/
│   ├── scripts/
│   │   ├── enrich_stocks.py             # Main enrichment script ⭐
│   │   ├── update_indices.py            # Update index memberships
│   │   ├── view_shareholding.py         # View shareholding data
│   │   ├── view_history.py              # View historical changes
│   │   └── view_timeseries.py           # View quarterly data
│   │
│   ├── data_fetch/                      # NSE data fetching
│   ├── preprocessing/                    # Data preprocessing
│   ├── analysis/                         # Technical analysis
│   └── visualization/                    # Charts and plots
│
├── docs/                                 # Documentation
├── examples/                             # Usage examples
└── output/                               # Generated reports/charts
```

## 📖 Documentation

- **[Enrichment Filtering Guide](docs/ENRICHMENT_FILTERING_GUIDE.md)** - Filter stocks by index, market cap
- **[Stock Data Access Guide](docs/STOCK_DATA_ACCESS_GUIDE.md)** - Access enriched metadata programmatically
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Command quick reference

## 🔍 Advanced Usage

### Filtering Options

```bash
# Combine multiple filters
python src/scripts/enrich_stocks.py \
  --index "NIFTY SMALLCAP 100" \
  --market-cap-min 1000 \
  --market-cap-max 5000 \
  --filter-enriched

# Resume from specific stock
python src/scripts/enrich_stocks.py --resume BANDHANBNK

# Limit number of stocks
python src/scripts/enrich_stocks.py --limit 50
```

### Programmatic Access

```python
import json

# Load enriched metadata
with open('data/metadata/stocks_metadata.json', 'r') as f:
    stocks = json.load(f)

# Access stock data
reliance = stocks['RELIANCE']
print(f"Market Cap: {reliance['MARKET_CAP']} Cr")
print(f"Sector: {reliance['SECTOR']}")
print(f"ROE: {reliance['ROE']}%")

# Access shareholding pattern
for holding in reliance['SHAREHOLDING_PATTERN']:
    if holding['type'] == 'Promoters':
        print(f"{holding['quarter']}: {holding['percentage']}")
```

## 🤝 Key Improvements

### Recent Fixes (Dec 2025)
- ✅ **Fixed consolidated page issue** - Banks now correctly fetch from standalone pages
- ✅ **Empty value filtering** - No more blank fields stored
- ✅ **NSE fallback** - Missing data filled from NSE API
- ✅ **Smart filtering** - Direct queries without temporary files
- ✅ **Removed Moneycontrol** - Unreliable 403 errors
- ✅ **Cleaned project structure** - Removed obsolete scripts and docs

## 📝 Notes

- **Rate Limiting**: 3-second delay between requests to Screener.in
- **Data Sources**: Primary: Screener.in | Fallback: NSE API
- **Backup**: Automatic backup before each enrichment run
- **Environment**: Use `conda activate mkt` before running scripts

## 🐛 Troubleshooting

### Module not found
```bash
# Ensure mkt environment is active
conda activate mkt

# Reinstall dependencies
pip install -r requirements.txt
```

### Empty market cap for banks
This is expected - some banks have empty data on Screener.in's consolidated pages. The script automatically tries standalone pages as fallback.

## 📄 License

MIT License - See LICENSE file for details

---

**Last Updated**: December 2025  
**Python Version**: 3.14  
**Environment**: Conda (mkt)
