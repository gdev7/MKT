"""
Example: Portfolio Backtesting with Custom Strategies

This demonstrates how to create and backtest portfolio strategies with
realistic constraints like trade limits, position sizing, and costs.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from datetime import datetime, timedelta
from src.strategy.portfolio_backtester import (
    PortfolioBacktester, 
    PortfolioConfig, 
    PositionSizing
)
from src.strategy.base_strategy import BaseStrategy, Signal, TradeAction
from src.data_fetch.data_fetcher import DataFetcher
from src.utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# EXAMPLE STRATEGY 1: RSI Mean Reversion
# ============================================================================

class RSIMeanReversionStrategy(BaseStrategy):
    """
    Buy when RSI < 30 (oversold), sell when RSI > 70 (overbought).
    """
    
    def __init__(self, rsi_period=14, oversold=30, overbought=70):
        super().__init__(name="RSI Mean Reversion")
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signals(self, data: pd.DataFrame) -> list:
        """Generate buy/sell signals based on RSI."""
        if len(data) < self.rsi_period + 1:
            return []
        
        # Calculate RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        signals = []
        position = None  # Track if we have a position
        
        for i in range(self.rsi_period, len(data)):
            date = data.index[i]
            price = data['Close'].iloc[i]
            current_rsi = rsi.iloc[i]
            
            # Buy signal: RSI crosses below oversold
            if current_rsi < self.oversold and position is None:
                signals.append(Signal(
                    date=date,
                    action=TradeAction.BUY,
                    price=price,
                    reason=f'RSI Oversold ({current_rsi:.1f})'
                ))
                position = 'long'
            
            # Sell signal: RSI crosses above overbought
            elif current_rsi > self.overbought and position == 'long':
                signals.append(Signal(
                    date=date,
                    action=TradeAction.SELL,
                    price=price,
                    reason=f'RSI Overbought ({current_rsi:.1f})'
                ))
                position = None
        
        return signals


# ============================================================================
# EXAMPLE STRATEGY 2: Moving Average Crossover
# ============================================================================

class MACrossoverStrategy(BaseStrategy):
    """
    Buy when fast MA crosses above slow MA.
    Sell when fast MA crosses below slow MA.
    """
    
    def __init__(self, fast_period=20, slow_period=50):
        super().__init__(name="MA Crossover")
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def generate_signals(self, data: pd.DataFrame) -> list:
        """Generate signals based on MA crossover."""
        if len(data) < self.slow_period + 1:
            return []
        
        # Calculate MAs
        fast_ma = data['Close'].rolling(window=self.fast_period).mean()
        slow_ma = data['Close'].rolling(window=self.slow_period).mean()
        
        signals = []
        position = None
        
        for i in range(self.slow_period, len(data)):
            date = data.index[i]
            price = data['Close'].iloc[i]
            
            prev_fast = fast_ma.iloc[i-1]
            prev_slow = slow_ma.iloc[i-1]
            curr_fast = fast_ma.iloc[i]
            curr_slow = slow_ma.iloc[i]
            
            # Bullish crossover
            if prev_fast <= prev_slow and curr_fast > curr_slow and position is None:
                signals.append(Signal(
                    date=date,
                    action=TradeAction.BUY,
                    price=price,
                    reason=f'Bullish MA Cross (Fast: {curr_fast:.2f}, Slow: {curr_slow:.2f})'
                ))
                position = 'long'
            
            # Bearish crossover
            elif prev_fast >= prev_slow and curr_fast < curr_slow and position == 'long':
                signals.append(Signal(
                    date=date,
                    action=TradeAction.SELL,
                    price=price,
                    reason=f'Bearish MA Cross (Fast: {curr_fast:.2f}, Slow: {curr_slow:.2f})'
                ))
                position = None
        
        return signals


# ============================================================================
# EXAMPLE STRATEGY 3: Momentum Breakout
# ============================================================================

class MomentumBreakoutStrategy(BaseStrategy):
    """
    Buy when price breaks above recent high with strong volume.
    Sell after holding period or stop loss.
    """
    
    def __init__(self, lookback=20, volume_multiplier=1.5, holding_days=10, stop_loss_pct=5):
        super().__init__(name="Momentum Breakout")
        self.lookback = lookback
        self.volume_multiplier = volume_multiplier
        self.holding_days = holding_days
        self.stop_loss_pct = stop_loss_pct
    
    def generate_signals(self, data: pd.DataFrame) -> list:
        """Generate signals based on breakout."""
        if len(data) < self.lookback + 1:
            return []
        
        signals = []
        position_entry = None
        position_price = None
        
        for i in range(self.lookback, len(data)):
            date = data.index[i]
            price = data['Close'].iloc[i]
            volume = data['Volume'].iloc[i]
            
            # Calculate metrics
            recent_high = data['High'].iloc[i-self.lookback:i].max()
            avg_volume = data['Volume'].iloc[i-self.lookback:i].mean()
            
            # Buy: Breakout above recent high with volume
            if position_entry is None:
                if price > recent_high and volume > avg_volume * self.volume_multiplier:
                    signals.append(Signal(
                        date=date,
                        action=TradeAction.BUY,
                        price=price,
                        reason=f'Breakout (High: {recent_high:.2f}, Vol: {volume/avg_volume:.1f}x)'
                    ))
                    position_entry = date
                    position_price = price
            
            # Sell: Holding period reached or stop loss
            else:
                days_held = (date - position_entry).days
                pnl_pct = ((price - position_price) / position_price) * 100
                
                if days_held >= self.holding_days or pnl_pct <= -self.stop_loss_pct:
                    reason = f'Exit after {days_held} days' if days_held >= self.holding_days else f'Stop Loss ({pnl_pct:.1f}%)'
                    signals.append(Signal(
                        date=date,
                        action=TradeAction.SELL,
                        price=price,
                        reason=reason
                    ))
                    position_entry = None
                    position_price = None
        
        return signals


# ============================================================================
# BACKTESTING EXAMPLES
# ============================================================================

def example_1_basic_backtest():
    """Example 1: Basic backtest with fixed position sizing."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Backtest - RSI Mean Reversion")
    print("="*70)
    
    # Configuration
    config = PortfolioConfig(
        initial_capital=1000000,  # 10 Lakhs
        position_size_method=PositionSizing.FIXED_AMOUNT,
        position_size_value=100000,  # 1 Lakh per position
        max_trades_per_week=5,
        max_trades_per_month=20,
        max_positions=10
    )
    
    # Strategy
    strategy = RSIMeanReversionStrategy(rsi_period=14, oversold=30, overbought=70)
    
    # Load data (example with a few stocks)
    fetcher = DataFetcher(use_multi_source=True)
    symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']
    
    data = {}
    for symbol in symbols:
        df = pd.read_csv(f'data/raw/{symbol}.csv', parse_dates=['Date'], index_col='Date')
        data[symbol] = df
    
    # Run backtest
    backtester = PortfolioBacktester(strategy, config)
    results = backtester.run(
        data,
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    
    # Print results
    print(f"\nInitial Capital: ₹{results['initial_value']:,.2f}")
    print(f"Final Value:     ₹{results['final_value']:,.2f}")
    print(f"Total Return:    ₹{results['total_return']:,.2f} ({results['total_return_pct']:.2f}%)")
    print(f"\nTotal Trades:    {results['total_trades']}")
    print(f"Winning Trades:  {results['winning_trades']}")
    print(f"Losing Trades:   {results['losing_trades']}")
    print(f"Win Rate:        {results['win_rate']:.2f}%")
    print(f"Profit Factor:   {results['profit_factor']:.2f}")
    print(f"Avg Holding:     {results['avg_holding_days']:.1f} days")
    
    # Show trades
    trades_df = backtester.get_trades_df()
    if not trades_df.empty:
        print(f"\nSample Trades:")
        print(trades_df.head(10).to_string(index=False))


def example_2_equal_weight():
    """Example 2: Equal weight position sizing."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Equal Weight Portfolio - MA Crossover")
    print("="*70)
    
    config = PortfolioConfig(
        initial_capital=2000000,  # 20 Lakhs
        position_size_method=PositionSizing.EQUAL_WEIGHT,
        max_positions=8,  # Divide capital equally among 8 positions
        max_trades_per_week=3,
        max_trades_per_month=12
    )
    
    strategy = MACrossoverStrategy(fast_period=20, slow_period=50)
    
    # Load more stocks
    symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 
               'BHARTIARTL', 'SBIN', 'LT', 'AXISBANK', 'MARUTI']
    
    # ... similar data loading and backtesting ...
    
    print("\nEqual weight configuration ensures balanced portfolio allocation")


def example_3_multi_strategy_comparison():
    """Example 3: Compare multiple strategies."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Strategy Comparison")
    print("="*70)
    
    strategies = [
        ("RSI Mean Reversion", RSIMeanReversionStrategy()),
        ("MA Crossover", MACrossoverStrategy()),
        ("Momentum Breakout", MomentumBreakoutStrategy())
    ]
    
    config = PortfolioConfig(
        initial_capital=1000000,
        position_size_method=PositionSizing.FIXED_AMOUNT,
        position_size_value=100000,
        max_positions=10
    )
    
    # ... load data ...
    
    results_comparison = []
    for name, strategy in strategies:
        # backtester = PortfolioBacktester(strategy, config)
        # results = backtester.run(data, start_date, end_date)
        # results_comparison.append((name, results))
        print(f"Testing {name}...")
    
    print("\nStrategy comparison helps identify best approach for your market conditions")


if __name__ == "__main__":
    print("="*70)
    print("PORTFOLIO BACKTESTING EXAMPLES")
    print("="*70)
    print("\nThese examples demonstrate how to:")
    print("1. Create custom trading strategies")
    print("2. Configure portfolio constraints (capital, position sizing, trade limits)")
    print("3. Run realistic backtests with costs and slippage")
    print("4. Analyze performance metrics")
    
    # Run examples (uncomment to execute)
    # example_1_basic_backtest()
    # example_2_equal_weight()
    # example_3_multi_strategy_comparison()
    
    print("\n" + "="*70)
    print("Uncomment the examples you want to run!")
    print("="*70)
