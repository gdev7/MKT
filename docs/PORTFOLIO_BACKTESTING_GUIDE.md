# Portfolio Backtesting Framework - Quick Guide

## Overview

Complete framework for backtesting trading strategies with realistic portfolio management, position sizing, trade limits, and transaction costs.

## Key Components

### 1. PortfolioConfig
Defines all portfolio constraints and parameters:

```python
config = PortfolioConfig(
    # Capital
    initial_capital=1000000,  # ₹10 Lakhs
    
    # Position Sizing
    position_size_method=PositionSizing.FIXED_AMOUNT,
    position_size_value=100000,  # ₹1 Lakh per trade
    
    # Trade Limits
    max_trades_per_week=5,
    max_trades_per_month=20,
    max_positions=10,  # Max concurrent positions
    
    # Risk Management
    max_position_size_pct=0.20,  # Max 20% per position
    reserve_cash_pct=0.10,  # Keep 10% cash reserve
    
    # Costs (realistic Indian market costs)
    brokerage_pct=0.0003,  # 0.03%
    transaction_charges_pct=0.0003,
    stt_pct=0.001,  # 0.1% on sell
    slippage_pct=0.001  # 0.1%
)
```

### 2. Position Sizing Methods

**Fixed Amount** (Default)
```python
position_size_method=PositionSizing.FIXED_AMOUNT
position_size_value=100000  # ₹1 Lakh per trade
```

**Equal Weight**
```python
position_size_method=PositionSizing.EQUAL_WEIGHT
max_positions=10  # Divides capital equally among 10 positions
```

**Percentage Based**
```python
position_size_method=PositionSizing.PERCENTAGE
position_size_value=10  # 10% of portfolio per position
```

### 3. Creating Strategies

Your strategy must inherit from `BaseStrategy` and implement `generate_signals()`:

```python
from src.strategy.base_strategy import BaseStrategy, Signal

class MyStrategy(BaseStrategy):
    def __init__(self, param1, param2):
        super().__init__(name="My Strategy")
        self.param1 = param1
        self.param2 = param2
    
    def generate_signals(self, data: pd.DataFrame) -> list:
        """
        Generate buy/sell signals.
        
        Args:
            data: OHLCV DataFrame with DatetimeIndex
        
        Returns:
            List of Signal objects
        """
        signals = []
        
        # Your strategy logic here
        # Example: Buy when condition met
        if some_condition:
            signals.append(Signal(
                date=current_date,
                action=TradeAction.BUY,
                price=current_price,
                reason='Why buying'  # Optional
            ))
        
        # Sell when condition met
        if some_other_condition:
            signals.append(Signal(
                date=current_date,
                action=TradeAction.SELL,
                price=current_price,
                reason='Why selling'
            ))
        
        return signals
```

### 4. Running Backtest

```python
from src.strategy.portfolio_backtester import PortfolioBacktester

# Create strategy and config
strategy = MyStrategy(param1=value1, param2=value2)
config = PortfolioConfig(initial_capital=1000000)

# Load historical data
data = {
    'RELIANCE': df_reliance,  # DataFrame with OHLCV
    'TCS': df_tcs,
    'INFY': df_infy,
    # ... more stocks
}

# Run backtest
backtester = PortfolioBacktester(strategy, config)
results = backtester.run(
    data,
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2024, 12, 31)
)

# View results
print(f"Return: {results['total_return_pct']:.2f}%")
print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Total Trades: {results['total_trades']}")
```

### 5. Analyzing Results

```python
# Get comprehensive metrics
print(f"Initial Capital: ₹{results['initial_value']:,.2f}")
print(f"Final Value: ₹{results['final_value']:,.2f}")
print(f"Total Return: {results['total_return_pct']:.2f}%")
print(f"Total Trades: {results['total_trades']}")
print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Profit Factor: {results['profit_factor']:.2f}")
print(f"Avg Holding: {results['avg_holding_days']:.1f} days")

# Get trade-by-trade details
trades_df = backtester.get_trades_df()
print(trades_df.head())

# Columns: Symbol, Entry Date, Entry Price, Exit Date, Exit Price,
#          Quantity, Invested, Exit Amount, P&L, P&L %, Holding Days
```

## Example Strategy Templates

### Template 1: Indicator-Based
```python
class IndicatorStrategy(BaseStrategy):
    def generate_signals(self, data: pd.DataFrame) -> list:
        # Calculate indicators
        rsi = calculate_rsi(data['Close'])
        macd = calculate_macd(data['Close'])
        
        signals = []
        position = None
        
        for i in range(len(data)):
            # Buy rule
            if rsi[i] < 30 and macd[i] > 0 and position is None:
                signals.append(Signal(..., action=TradeAction.BUY))
                position = 'long'
            
            # Sell rule
            elif rsi[i] > 70 and position == 'long':
                signals.append(Signal(..., action=TradeAction.SELL))
                position = None
        
        return signals
```

### Template 2: Pattern-Based
```python
class PatternStrategy(BaseStrategy):
    def generate_signals(self, data: pd.DataFrame) -> list:
        signals = []
        
        for i in range(20, len(data)):
            # Detect breakout pattern
            recent_high = data['High'][i-20:i].max()
            if data['Close'][i] > recent_high:
                signals.append(Signal(..., action=TradeAction.BUY))
            
            # Exit after N days
            # (track holding in your logic)
        
        return signals
```

### Template 3: Multi-Timeframe
```python
class MultiTimeframeStrategy(BaseStrategy):
    def generate_signals(self, data: pd.DataFrame) -> list:
        # Resample to weekly
        weekly = data.resample('W').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        })
        
        # Weekly trend
        weekly_trend = weekly['Close'].rolling(10).mean()
        
        # Generate daily signals aligned with weekly trend
        signals = []
        # ... your logic
        return signals
```

## Best Practices

### 1. Strategy Design
- Keep strategies simple and testable
- Avoid look-ahead bias (don't use future data)
- Include clear entry and exit rules
- Consider transaction costs in logic

### 2. Position Sizing
- Start with fixed amount for simplicity
- Use equal weight for diversification
- Percentage-based for dynamic allocation

### 3. Risk Management
- Set `max_positions` to limit exposure
- Use `reserve_cash_pct` to avoid being fully invested
- Implement stop losses in strategy logic

### 4. Trade Limits
- `max_trades_per_week`: Avoid overtrading
- `max_trades_per_month`: Control monthly activity
- Helps simulate realistic trading behavior

### 5. Backtesting Period
- Use at least 2-3 years of data
- Include different market conditions (bull, bear, sideways)
- Test on out-of-sample data

### 6. Performance Analysis
- Don't just focus on returns
- Check win rate, profit factor, drawdown
- Analyze trade distribution
- Look at holding period

## Common Workflows

### Workflow 1: Single Strategy Test
1. Create strategy class
2. Configure portfolio parameters
3. Load historical data for stocks
4. Run backtest
5. Analyze results
6. Refine strategy based on insights

### Workflow 2: Strategy Comparison
1. Create multiple strategy variants
2. Use same config for fair comparison
3. Run each on same data period
4. Compare metrics (return, win rate, etc.)
5. Select best performer

### Workflow 3: Parameter Optimization
1. Define strategy with parameters
2. Create parameter grid
3. Run backtest for each combination
4. Track performance metrics
5. Identify optimal parameters

### Workflow 4: Walk-Forward Testing
1. Divide data into periods
2. Train/optimize on first period
3. Test on next period
4. Roll forward and repeat
5. Validate robustness

## Transaction Costs

Realistic costs are included automatically:

**Buy Trade:**
- Brokerage: 0.03%
- Transaction charges: 0.03%
- Slippage: 0.1%
- **Total buy cost: ~0.16%**

**Sell Trade:**
- Brokerage: 0.03%
- Transaction charges: 0.03%
- STT: 0.1%
- Slippage: 0.1%
- **Total sell cost: ~0.26%**

**Round-trip cost: ~0.42%**

These are configurable in `PortfolioConfig`.

## Files Structure

```
src/strategy/
├── base_strategy.py           # Base class for all strategies
├── portfolio_backtester.py    # Main backtesting engine
├── backtester.py              # Simple backtester (existing)
└── example_strategies.py      # Example implementations

examples/
└── portfolio_backtest_examples.py  # Usage examples
```

## Next Steps

1. **Create your first strategy**
   - Start with simple indicator-based rules
   - Test with 2-3 stocks first

2. **Run initial backtest**
   - Use realistic parameters
   - Check if signals are being generated

3. **Analyze results**
   - Review trades DataFrame
   - Check win rate and holding periods

4. **Refine strategy**
   - Adjust parameters
   - Add filters or conditions
   - Re-test

5. **Scale up**
   - Test with more stocks
   - Try different market conditions
   - Compare with other strategies

## Support

For questions or issues:
- Check `examples/portfolio_backtest_examples.py`
- Review strategy templates above
- See `docs/` for detailed guides
