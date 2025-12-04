# Candlestick Visualization Guide

## Quick Start

```python
from src.data_fetch.stock_data_reader import StockDataReader
from src.visualization.candlestick_visualizer import CandlestickVisualizer

# Load data
reader = StockDataReader('data/raw/3MINDIA.csv')
data = reader.get_by_year(2024)

# Create visualizer
visualizer = CandlestickVisualizer(data, symbol='3MINDIA')

# Create and show chart
fig = visualizer.plot_daily(show_volume=True, moving_averages=[20, 50])
fig.show()
```

## All Timeframes

### 1. Daily Candlesticks
```python
fig = visualizer.plot_daily(
    show_volume=True,
    moving_averages=[20, 50, 200],
    show_rangeslider=True
)
fig.show()
```

### 2. Weekly Candlesticks
```python
fig = visualizer.plot_weekly(
    show_volume=True,
    moving_averages=[10, 20],
    height=900
)
fig.show()
```

### 3. Monthly Candlesticks
```python
fig = visualizer.plot_monthly(
    show_volume=True,
    moving_averages=[6, 12],
    height=900
)
fig.show()
```

### 4. Quarterly Candlesticks
```python
fig = visualizer.plot_quarterly(
    show_volume=True,
    moving_averages=[4, 8],
    height=900
)
fig.show()
```

### 5. Yearly Candlesticks
```python
fig = visualizer.plot_yearly(
    show_volume=True,
    moving_averages=[3, 5],
    height=900
)
fig.show()
```

## Using Generic Method

```python
# All these create weekly charts
fig = visualizer.plot_candlestick(timeframe='W')
fig = visualizer.plot_candlestick(timeframe='week')
fig = visualizer.plot_candlestick(timeframe='weekly')
```

### Timeframe Options
- **Daily**: 'D', 'day', 'daily', 'd'
- **Weekly**: 'W', 'week', 'weekly', 'w'
- **Monthly**: 'M', 'month', 'monthly', 'm'
- **Quarterly**: 'Q', 'quarter', 'quarterly', 'q'
- **Yearly**: 'Y', 'year', 'yearly', 'y', 'a'

## Customization Options

### Without Volume
```python
fig = visualizer.plot_daily(
    show_volume=False,
    moving_averages=[20, 50, 200]
)
```

### Classic Color Scheme
```python
fig = visualizer.plot_weekly(
    color_scheme='classic',  # Black & white
    show_volume=True
)
```

### Custom Title and Height
```python
fig = visualizer.plot_monthly(
    title='My Custom Chart Title',
    height=1000,
    show_rangeslider=False
)
```

### Multiple Moving Averages
```python
fig = visualizer.plot_daily(
    moving_averages=[10, 20, 50, 100, 200],
    show_volume=True
)
```

## Multi-Timeframe Comparison

```python
fig = visualizer.create_comparison_chart(
    timeframes=['D', 'W', 'M'],
    moving_averages=[20, 50],
    height=1400
)
fig.show()
```

## Saving Charts

### Save as HTML (Interactive)
```python
fig = visualizer.plot_weekly()
visualizer.save_chart(fig, 'weekly_chart.html')
```

### Save as PNG (Static)
```python
visualizer.save_chart(
    fig,
    'weekly_chart.png',
    format='png',
    width=1920,
    height=1080
)
```

### Supported Formats
- `'html'` - Interactive HTML file (recommended)
- `'png'` - PNG image
- `'jpg'` - JPEG image
- `'svg'` - SVG vector image
- `'pdf'` - PDF document

## Complete Example

```python
from src.data_fetch.stock_data_reader import StockDataReader
from src.visualization.candlestick_visualizer import CandlestickVisualizer

# Load stock data
reader = StockDataReader('data/raw/RELIANCE.csv')

# Get 2024 data
data_2024 = reader.get_by_year(2024)

# Create visualizer
visualizer = CandlestickVisualizer(data_2024, symbol='RELIANCE')

# Create daily chart with volume and MAs
fig_daily = visualizer.plot_daily(
    title='RELIANCE - Daily Chart 2024',
    show_volume=True,
    moving_averages=[20, 50, 200],
    height=900
)

# Save and show
visualizer.save_chart(fig_daily, 'output/reliance_daily.html')
fig_daily.show()

# Create weekly chart
fig_weekly = visualizer.plot_weekly(
    show_volume=True,
    moving_averages=[10, 20],
    height=900
)

# Save
visualizer.save_chart(fig_weekly, 'output/reliance_weekly.html')
```

## Interactive Features

When viewing HTML charts in a browser:

- **Zoom**: Click and drag on the chart
- **Pan**: Hold Shift and drag
- **Hover**: Move mouse over candles for OHLC details
- **Reset**: Double-click anywhere to reset zoom
- **Toggle**: Click legend items to show/hide traces
- **Download**: Use camera icon to download as PNG

## Common Use Cases

### 1. Recent Performance Analysis
```python
# Get last 90 days
recent_data = reader.get_lookback('2024-12-31', days=90)
visualizer = CandlestickVisualizer(recent_data, 'STOCK')
fig = visualizer.plot_daily(moving_averages=[10, 20, 50])
fig.show()
```

### 2. Quarterly Review
```python
# Get Q1 2024
q1_data = reader.get_by_quarter(2024, 1)
visualizer = CandlestickVisualizer(q1_data, 'STOCK')
fig = visualizer.plot_daily(show_volume=True)
fig.show()
```

### 3. Long-Term Analysis
```python
# Get 5 years of data
data_5y = reader.get_date_range('2020-01-01', '2024-12-31')
visualizer = CandlestickVisualizer(data_5y, 'STOCK')
fig = visualizer.plot_monthly(moving_averages=[6, 12])
fig.show()
```

### 4. Compare Multiple Timeframes
```python
data = reader.get_by_year([2023, 2024])
visualizer = CandlestickVisualizer(data, 'STOCK')
fig = visualizer.create_comparison_chart(['D', 'W', 'M'])
fig.show()
```

## Running Examples

```bash
conda activate mkt
cd /mnt/c/Users/ProsunHalder/Videos/MKT
python examples/candlestick_visualization_examples.py
```

This will create 12 different chart examples in `output/charts/` directory.

## Chart Files Created

After running the examples, you'll find:
- `daily_candlestick.html` - Daily chart with MAs
- `weekly_candlestick.html` - Weekly chart
- `monthly_candlestick.html` - Monthly chart
- `quarterly_candlestick.html` - Quarterly chart
- `yearly_candlestick.html` - Yearly chart
- `daily_no_volume.html` - Chart without volume
- `weekly_classic_colors.html` - Classic color scheme
- `multi_timeframe_comparison.html` - Multiple timeframes
- `q1_2024_daily.html` - Q1 2024 analysis
- `recent_90_days.html` - Recent 90-day chart

## API Reference

### CandlestickVisualizer Class

**Constructor:**
```python
CandlestickVisualizer(data, symbol='Stock')
```

**Methods:**
- `plot_candlestick(timeframe, title, show_volume, moving_averages, height, show_rangeslider, color_scheme)` - Generic plotting method
- `plot_daily(**kwargs)` - Daily candlesticks
- `plot_weekly(**kwargs)` - Weekly candlesticks
- `plot_monthly(**kwargs)` - Monthly candlesticks
- `plot_quarterly(**kwargs)` - Quarterly candlesticks
- `plot_yearly(**kwargs)` - Yearly candlesticks
- `create_comparison_chart(timeframes, moving_averages, height)` - Multi-timeframe comparison
- `save_chart(fig, filename, format, width, height)` - Save chart to file

**Parameters:**
- `timeframe`: str - Timeframe for candlesticks
- `title`: str - Chart title
- `show_volume`: bool - Show volume bars (default: True)
- `moving_averages`: list - MA periods (e.g., [20, 50, 200])
- `height`: int - Chart height in pixels (default: 800)
- `show_rangeslider`: bool - Show range slider (default: True)
- `color_scheme`: str - 'default' or 'classic'

## Tips

1. **Performance**: For large datasets, use weekly/monthly timeframes
2. **Clarity**: Limit moving averages to 3-4 for better readability
3. **Comparison**: Use multi-timeframe charts to spot trends
4. **Interactivity**: HTML format preserves all interactive features
5. **Sharing**: Export to PNG for presentations/reports
