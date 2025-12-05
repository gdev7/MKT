# Stock Enrichment Filtering Guide

## Overview

The enrichment script now supports **smart filtering** to enrich specific subsets of stocks without requiring temporary files. Filters are applied directly from `stocks_metadata.json`.

## Available Filters

### 1. Filter by Index

Enrich all stocks belonging to a specific index:

```bash
# NIFTY SMALLCAP 100
python src/scripts/enrich_screener_complete.py --index "NIFTY SMALLCAP 100"

# NIFTY 50
python src/scripts/enrich_screener_complete.py --index "NIFTY 50"

# NIFTY MIDCAP 100
python src/scripts/enrich_screener_complete.py --index "NIFTY MIDCAP 100"

# NIFTY NEXT 50
python src/scripts/enrich_screener_complete.py --index "NIFTY NEXT 50"
```

**How it works:**
- Reads `INDICES` field from each stock in metadata
- Selects stocks where the specified index is present
- No temporary file generation required

### 2. Filter by Market Cap Range

Enrich stocks within a specific market cap range (in Crores):

```bash
# Market cap between 1,000 - 10,000 Cr
python src/scripts/enrich_screener_complete.py --market-cap-min 1000 --market-cap-max 10000

# Market cap > 50,000 Cr (Large cap)
python src/scripts/enrich_screener_complete.py --market-cap-min 50000

# Market cap < 5,000 Cr (Small cap)
python src/scripts/enrich_screener_complete.py --market-cap-max 5000
```

**How it works:**
- Reads `MARKET_CAP` field from each stock
- Filters stocks within specified range
- **Note:** Only works on stocks that are already enriched (have MARKET_CAP field)

### 3. Filter Out Already Enriched

Skip stocks that already have enrichment data:

```bash
# Enrich only unenriched stocks from NIFTY SMALLCAP 100
python src/scripts/enrich_screener_complete.py --index "NIFTY SMALLCAP 100" --filter-enriched
```

**How it works:**
- Checks if stock has `MARKET_CAP` field (indicator of enrichment)
- Excludes stocks that are already enriched
- Useful for incremental enrichment or resuming interrupted runs

## Combining Filters

Filters can be combined for precise control:

```bash
# Enrich only unenriched stocks from NIFTY SMALLCAP 100
python src/scripts/enrich_screener_complete.py \
  --index "NIFTY SMALLCAP 100" \
  --filter-enriched

# Re-enrich large cap stocks (already enriched, for updates)
python src/scripts/enrich_screener_complete.py \
  --market-cap-min 50000

# Test with limit
python src/scripts/enrich_screener_complete.py \
  --index "NIFTY 50" \
  --limit 5
```

## All Command-Line Options

```
--index INDEX                 Filter by index name (e.g., "NIFTY SMALLCAP 100")
--market-cap-min MIN          Minimum market cap in Cr
--market-cap-max MAX          Maximum market cap in Cr
--filter-enriched             Skip already enriched stocks
--limit N                     Process only first N stocks (for testing)
--test                        Test mode: process only 5 stocks
--resume SYMBOL               Resume from specific symbol
```

## Usage Examples

### Example 1: Initial Enrichment of NIFTY SMALLCAP 100

```bash
# Enrich all 100 stocks
python src/scripts/enrich_screener_complete.py --index "NIFTY SMALLCAP 100"

# Output:
# Mode: FILTERED (100 stocks)
#   Index: NIFTY SMALLCAP 100
# Enriching 100 stocks...
```

### Example 2: Re-enrichment (Updates)

```bash
# Re-enrich to capture new quarterly data and shareholding changes
python src/scripts/enrich_screener_complete.py --index "NIFTY SMALLCAP 100"

# Only enrich stocks that are not yet enriched
python src/scripts/enrich_screener_complete.py --index "NIFTY SMALLCAP 100" --filter-enriched

# Output:
# Mode: FILTERED (97 stocks)
#   Index: NIFTY SMALLCAP 100
#   Filtered 3 already enriched
```

### Example 3: Market Cap Based Selection

```bash
# Find and enrich mid-cap stocks (10,000 - 50,000 Cr)
python src/scripts/enrich_screener_complete.py --market-cap-min 10000 --market-cap-max 50000

# Output:
# Mode: FILTERED (45 stocks)
#   Market Cap: 10000-50000 Cr
```

### Example 4: Test Before Full Run

```bash
# Test with 3 stocks first
python src/scripts/enrich_screener_complete.py --index "NIFTY SMALLCAP 100" --limit 3

# Output:
# Mode: FILTERED (100 stocks)
#   Index: NIFTY SMALLCAP 100
# Processing first 3 stocks (test mode)
```

## Finding Stocks by Criteria

Use Python to query `stocks_metadata.json` for stocks matching specific criteria:

### Query 1: Find All Indices

```python
import json

with open('data/metadata/stocks_metadata.json', 'r') as f:
    data = json.load(f)

# Get all unique indices
all_indices = set()
for stock in data.values():
    all_indices.update(stock.get('INDICES', []))

print('Available indices:')
for idx in sorted(all_indices):
    count = sum(1 for s in data.values() if idx in s.get('INDICES', []))
    print(f'  {idx}: {count} stocks')
```

### Query 2: Find Stocks by Market Cap Range

```python
import json

with open('data/metadata/stocks_metadata.json', 'r') as f:
    data = json.load(f)

# Find stocks with market cap between 1,000 - 10,000 Cr
filtered = []
for symbol, stock in data.items():
    mc = stock.get('MARKET_CAP')
    if mc:
        try:
            val = float(str(mc).replace(',', ''))
            if 1000 <= val <= 10000:
                filtered.append((symbol, stock.get('NAME OF COMPANY'), val))
        except:
            pass

print(f'Found {len(filtered)} stocks')
for symbol, name, cap in sorted(filtered, key=lambda x: x[2]):
    print(f'{symbol:15} {name[:40]:40} {cap:>10,.0f} Cr')
```

### Query 3: Find Unenriched Stocks from Index

```python
import json

with open('data/metadata/stocks_metadata.json', 'r') as f:
    data = json.load(f)

index_name = "NIFTY SMALLCAP 100"

# Find stocks in index
in_index = [s for s, stock in data.items() if index_name in stock.get('INDICES', [])]

# Find which are not enriched
unenriched = [s for s in in_index if 'MARKET_CAP' not in data[s]]

print(f'{index_name}:')
print(f'  Total: {len(in_index)}')
print(f'  Enriched: {len(in_index) - len(unenriched)}')
print(f'  Pending: {len(unenriched)}')
```

## Workflow: Enriching by Index

### Step 1: Check Status

```bash
# Check how many stocks need enrichment
python -c "
import json
with open('data/metadata/stocks_metadata.json') as f:
    data = json.load(f)
idx = 'NIFTY SMALLCAP 100'
total = sum(1 for s in data.values() if idx in s.get('INDICES', []))
enriched = sum(1 for s in data.values() if idx in s.get('INDICES', []) and 'MARKET_CAP' in s)
print(f'{idx}: {enriched}/{total} enriched')
"
```

### Step 2: Test Run

```bash
# Test with 3 stocks
python src/scripts/enrich_screener_complete.py --index "NIFTY SMALLCAP 100" --limit 3
```

### Step 3: Full Enrichment

```bash
# Enrich all unenriched stocks
python src/scripts/enrich_screener_complete.py --index "NIFTY SMALLCAP 100" --filter-enriched
```

### Step 4: Verify

```bash
# Check completion
python -c "
import json
with open('data/metadata/stocks_metadata.json') as f:
    data = json.load(f)
idx = 'NIFTY SMALLCAP 100'
stocks = [s for s in data if idx in data[s].get('INDICES', [])]
with_cap = [s for s in stocks if 'MARKET_CAP' in data[s]]
with_shareholding = [s for s in stocks if 'SHAREHOLDING_PATTERN' in data[s]]
print(f'{idx}:')
print(f'  Total: {len(stocks)}')
print(f'  With Market Cap: {len(with_cap)}')
print(f'  With Shareholding: {len(with_shareholding)}')
"
```

## Performance

- **Index filtering**: Instant (reads from metadata)
- **Market cap filtering**: Instant (reads from metadata)
- **Enrichment**: ~3 seconds per stock
- **NIFTY SMALLCAP 100**: ~5 minutes for 100 stocks
- **NIFTY 50**: ~2.5 minutes for 50 stocks

## Best Practices

1. **Always test first**: Use `--limit 3` to verify filters work correctly
2. **Use --filter-enriched for updates**: Avoid re-enriching already done stocks
3. **Monitor progress**: Script saves after every stock, safe to interrupt
4. **Resume on failure**: Use `--resume SYMBOL` if interrupted
5. **Backup created automatically**: Saved to `stocks_metadata_backup_complete.json`

## Common Patterns

```bash
# Pattern 1: Fresh enrichment of an index
python src/scripts/enrich_screener_complete.py --index "NIFTY 50"

# Pattern 2: Update existing enrichment
python src/scripts/enrich_screener_complete.py --index "NIFTY SMALLCAP 100"

# Pattern 3: Only enrich new stocks
python src/scripts/enrich_screener_complete.py --index "NIFTY MIDCAP 100" --filter-enriched

# Pattern 4: Re-enrich large caps for updates
python src/scripts/enrich_screener_complete.py --market-cap-min 50000

# Pattern 5: Test before full run
python src/scripts/enrich_screener_complete.py --index "NIFTY NEXT 50" --limit 5
```

## No Temporary Files Needed

✅ All filtering done in-memory from `stocks_metadata.json`  
✅ No `.txt` files or intermediate storage required  
✅ Clean, efficient, and scriptable  
✅ Easy to integrate into automated workflows
