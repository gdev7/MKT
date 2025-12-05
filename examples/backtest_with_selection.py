"""
Portfolio Backtesting with Stock Selection Examples.

Demonstrates backtesting strategies on different stock universes.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from src.strategy.portfolio_backtester import PortfolioBacktester, PortfolioConfig, PositionSizing
from src.strategy.example_strategies import MovingAverageCrossoverStrategy, RSIStrategy


def example_1_backtest_nifty50():
    """Example 1: Backtest on NIFTY 50 stocks."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Backtest on NIFTY 50")
    print("="*70)
    
    # Configuration
    config = PortfolioConfig(
        initial_capital=2000000,  # 20 Lakhs
        position_size_method=PositionSizing.FIXED_AMOUNT,
        position_size_value=200000,  # 2 Lakhs per position
        max_trades_per_week=5,
        max_trades_per_month=15,
        max_positions=10
    )
    
    # Strategy
    strategy = MovingAverageCrossoverStrategy(fast_period=20, slow_period=50)
    
    # Backtest on NIFTY 50
    backtester = PortfolioBacktester(strategy, config)
    results = backtester.run(
        selection_type='index',
        selection_value='NIFTY 50',
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    
    # Print results
    if results:
        print(f"\nNIFTY 50 Backtest Results:")
        print(f"  Initial Capital: ₹{results['initial_value']:,.2f}")
        print(f"  Final Value:     ₹{results['final_value']:,.2f}")
        print(f"  Total Return:    {results['total_return_pct']:.2f}%")
        print(f"  Total Trades:    {results['total_trades']}")
        print(f"  Win Rate:        {results['win_rate']:.2f}%")


def example_2_backtest_single_stock():
    """Example 2: Backtest on a single stock."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Backtest on Single Stock")
    print("="*70)
    
    config = PortfolioConfig(
        initial_capital=500000,  # 5 Lakhs
        position_size_method=PositionSizing.PERCENTAGE,
        position_size_value=100,  # 100% on single stock
        max_positions=1
    )
    
    strategy = RSIStrategy(period=14, oversold=30, overbought=70)
    
    # Backtest on RELIANCE only
    backtester = PortfolioBacktester(strategy, config)
    results = backtester.run(
        selection_type='single',
        selection_value='RELIANCE',
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    
    if results:
        print(f"\nRELIANCE Backtest Results:")
        print(f"  Return:          {results['total_return_pct']:.2f}%")
        print(f"  Trades:          {results['total_trades']}")
        print(f"  Win Rate:        {results['win_rate']:.2f}%")
        print(f"  Avg Holding:     {results['avg_holding_days']:.1f} days")


def example_3_backtest_custom_list():
    """Example 3: Backtest on custom stock list."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Backtest on Custom Stock List")
    print("="*70)
    
    config = PortfolioConfig(
        initial_capital=1000000,
        position_size_method=PositionSizing.EQUAL_WEIGHT,
        max_positions=5
    )
    
    strategy = MovingAverageCrossoverStrategy(fast_period=10, slow_period=30)
    
    # Custom list of IT stocks
    my_stocks = ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM']
    
    backtester = PortfolioBacktester(strategy, config)
    results = backtester.run(
        symbols=my_stocks,
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    
    if results:
        print(f"\nIT Stocks Backtest Results:")
        print(f"  Stocks:          {', '.join(my_stocks)}")
        print(f"  Return:          {results['total_return_pct']:.2f}%")
        print(f"  Trades:          {results['total_trades']}")
        print(f"  Win Rate:        {results['win_rate']:.2f}%")


def example_4_backtest_sector():
    """Example 4: Backtest on sector stocks."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Backtest on Sector")
    print("="*70)
    
    config = PortfolioConfig(
        initial_capital=1500000,
        position_size_method=PositionSizing.FIXED_AMOUNT,
        position_size_value=150000,
        max_positions=10,
        max_trades_per_month=20
    )
    
    strategy = RSIStrategy(period=14, oversold=30, overbought=70)
    
    # Backtest on Banking sector
    backtester = PortfolioBacktester(strategy, config)
    results = backtester.run(
        selection_type='sector',
        selection_value='Banking',
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    
    if results:
        print(f"\nBanking Sector Backtest Results:")
        print(f"  Return:          {results['total_return_pct']:.2f}%")
        print(f"  Trades:          {results['total_trades']}")
        print(f"  Win Rate:        {results['win_rate']:.2f}%")
        print(f"  Profit Factor:   {results['profit_factor']:.2f}")


def example_5_compare_indices():
    """Example 5: Compare performance across different indices."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Compare Performance Across Indices")
    print("="*70)
    
    config = PortfolioConfig(
        initial_capital=1000000,
        position_size_method=PositionSizing.FIXED_AMOUNT,
        position_size_value=100000,
        max_positions=10
    )
    
    strategy = MovingAverageCrossoverStrategy()
    
    indices = [
        ('NIFTY 50', 'Large Cap'),
        ('NIFTY MIDCAP 100', 'Mid Cap'),
        ('NIFTY SMALLCAP 100', 'Small Cap')
    ]
    
    print("\nComparing Strategy Performance Across Market Caps:")
    print("-"*70)
    print(f"{'Index':<25} {'Type':<15} {'Return %':>12} {'Win Rate':>12} {'Trades':>8}")
    print("-"*70)
    
    for index_name, cap_type in indices:
        backtester = PortfolioBacktester(strategy, config)
        results = backtester.run(
            selection_type='index',
            selection_value=index_name,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2024, 12, 31)
        )
        
        if results and results.get('total_trades', 0) > 0:
            print(f"{index_name:<25} {cap_type:<15} {results['total_return_pct']:>12.2f} {results['win_rate']:>11.2f}% {results['total_trades']:>8}")
        else:
            print(f"{index_name:<25} {cap_type:<15} {'N/A':>12} {'N/A':>12} {'0':>8}")


if __name__ == "__main__":
    print("="*70)
    print("PORTFOLIO BACKTESTING WITH STOCK SELECTION")
    print("="*70)
    print("\nThese examples show how to backtest on:")
    print("1. Index constituents (NIFTY 50, NIFTY 100, etc.)")
    print("2. Single stocks")
    print("3. Custom stock lists")
    print("4. Sector-based selection")
    print("5. Comparative analysis")
    
    # Uncomment examples to run
    # example_1_backtest_nifty50()
    # example_2_backtest_single_stock()
    # example_3_backtest_custom_list()
    # example_4_backtest_sector()
    # example_5_compare_indices()
    
    print("\n" + "="*70)
    print("Uncomment examples to run backtests!")
    print("="*70)
