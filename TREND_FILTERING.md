# Trend-Based Stock Filtering

Filter stocks based on market trend patterns: Uptrend (Bull), Downtrend (Bear), or Sideways (Consolidation).

## Quick Start

```bash
# Activate environment
conda activate mkt

# Analyze single stock
python src/analysis/trend_detector.py HDFCBANK

# Run examples
python examples/trend_filtering_examples.py
```

## Usage

### 1. Detect Trend for Single Stock

```python
from src.analysis.trend_detector import TrendDetector, TrendFilter

# Load stock data
trend_filter = TrendFilter()
df = trend_filter.load_stock_data("HDFCBANK")

# Detect trend
detector = TrendDetector()
trend_info = detector.detect_trend_with_strength(df, period=30)

print(f"Trend: {trend_info['trend'].value}")
print(f"Strength: {trend_info['strength']}")
print(f"R-Squared: {trend_info['r_squared']:.3f}")
```

### 2. Filter Uptrend Stocks

```python
from src.analysis.trend_detector import TrendFilter, TrendType

trend_filter = TrendFilter()

# Filter for uptrend
uptrend_stocks = trend_filter.filter_by_trend(
    symbols=['TCS', 'INFY', 'HDFCBANK', 'ICICIBANK'],
    trend_type=TrendType.UPTREND,
    period=20,
    min_strength=0.6
)

for stock in uptrend_stocks:
    print(f"{stock['symbol']}: {stock['price_change_pct']:+.2f}%")
```

### 3. Filter from Index

```python
import json

# Load metadata
with open('data/metadata/stocks_metadata.json', 'r') as f:
    metadata = json.load(f)

# Get NIFTY 50 stocks
nifty50 = [s for s, d in metadata.items() 
           if 'NIFTY 50' in d.get('INDICES', '')]

# Filter uptrend stocks
uptrend_stocks = trend_filter.filter_by_trend(
    symbols=nifty50,
    trend_type=TrendType.UPTREND,
    period=30,
    min_strength=0.7
)
```

## Trend Types

### 🟢 Uptrend (Bull Market)
- **Criteria**: Higher highs AND higher lows
- **Indicators**: Price consistently making new peaks
- **Use**: Buy signals, momentum trading

### 🔴 Downtrend (Bear Market)
- **Criteria**: Lower highs AND lower lows
- **Indicators**: Price consistently making new lows
- **Use**: Short signals, avoid buying

### 🟡 Sideways (Consolidation)
- **Criteria**: Neither uptrend nor downtrend
- **Indicators**: Price oscillating in range
- **Use**: Range trading, breakout opportunities

## Parameters

### Detection Period
```python
# Short-term: 20 days
trend = detector.detect_trend(df, period=20)

# Medium-term: 50 days
trend = detector.detect_trend(df, period=50)

# Long-term: 100 days
trend = detector.detect_trend(df, period=100)
```

### Trend Strength

```python
# Strict filtering (strong trends only)
stocks = trend_filter.filter_by_trend(
    symbols=symbols,
    trend_type=TrendType.UPTREND,
    min_strength=0.8  # R² > 0.8
)

# Relaxed filtering (weak trends accepted)
stocks = trend_filter.filter_by_trend(
    symbols=symbols,
    trend_type=TrendType.UPTREND,
    min_strength=0.5  # R² > 0.5
)
```

## Return Data

Each filtered stock returns:

```python
{
    'symbol': 'HDFCBANK',
    'trend': 'uptrend',
    'strength': 'strong',      # 'strong' if R² > 0.7, else 'weak'
    'r_squared': 0.845,        # Trend strength (0-1)
    'slope_pct': 2.5,          # Price slope percentage
    'price_change_pct': 8.5,   # Total price change %
    'current_price': 1234.50,
    'support': 1150.00,        # Support level
    'resistance': 1280.00      # Resistance level
}
```

## Support & Resistance

```python
# Get support and resistance levels
support, resistance = detector.get_support_resistance(df, period=50)

# Calculate range
range_pct = ((resistance - support) / support) * 100
print(f"Trading Range: {range_pct:.1f}%")
```

## Examples

See `examples/trend_filtering_examples.py` for:
1. Single stock trend detection
2. Filter uptrend from NIFTY 50
3. Find downtrend stocks
4. Identify sideways/consolidating stocks
5. Get all trend classifications
6. Filter by index membership

## Technical Details

### Swing Point Detection
- Uses local highs/lows with configurable period
- Default: 5-period swing detection
- Identifies pivot points for trend analysis

### Trend Strength (R²)
- Linear regression fit quality
- Range: 0 (weak) to 1 (strong)
- > 0.7 = Strong trend
- < 0.5 = Weak/unreliable trend

### Slope Calculation
- Price change per period normalized to percentage
- Positive = upward slope
- Negative = downward slope

## Command Line

```bash
# Analyze single stock
python src/analysis/trend_detector.py SYMBOL

# Examples
python src/analysis/trend_detector.py HDFCBANK
python src/analysis/trend_detector.py TCS
python src/analysis/trend_detector.py RELIANCE
```

## Integration with Stock Enrichment

```python
# Combine with enriched metadata
with open('data/metadata/stocks_metadata.json') as f:
    stocks = json.load(f)

# Filter high market cap stocks in uptrend
high_cap = [s for s, d in stocks.items() 
            if float(d.get('MARKET_CAP', 0) or 0) > 10000]

uptrend = trend_filter.filter_by_trend(
    symbols=high_cap,
    trend_type=TrendType.UPTREND,
    min_strength=0.7
)
```

---

**Created**: December 2025  
**Environment**: conda mkt  
**Dependencies**: pandas, numpy
