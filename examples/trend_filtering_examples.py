#!/usr/bin/env python3
"""
Trend-Based Stock Filtering Examples

Demonstrates how to filter stocks based on trend analysis.

Usage:
    python examples/trend_filtering_examples.py
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.trend_detector import TrendDetector, TrendFilter, TrendType


def example_1_detect_single_stock():
    """Example 1: Detect trend for a single stock"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Single Stock Trend Detection")
    print("="*70)
    
    symbol = "RELIANCE"
    trend_filter = TrendFilter()
    df = trend_filter.load_stock_data(symbol)
    
    if df is None:
        print(f"Error: Could not load data for {symbol}")
        return
    
    detector = TrendDetector()
    trend_info = detector.detect_trend_with_strength(df, period=30)
    support, resistance = detector.get_support_resistance(df, period=50)
    
    print(f"\nStock: {symbol}")
    print(f"Trend: {trend_info['trend'].value.upper()}")
    print(f"Strength: {trend_info['strength'].upper()}")
    print(f"R-Squared: {trend_info['r_squared']:.3f}")
    print(f"Slope: {trend_info['slope_pct']:.2f}%")
    print(f"Price Change: {trend_info['price_change_pct']:.2f}%")
    print(f"Current Price: ₹{trend_info['current_price']:.2f}")
    print(f"Support Level: ₹{support:.2f}")
    print(f"Resistance Level: ₹{resistance:.2f}")


def example_2_filter_uptrend_stocks():
    """Example 2: Filter stocks in uptrend from NIFTY 50"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Filter Uptrend Stocks from NIFTY 50")
    print("="*70)
    
    # Load NIFTY 50 symbols from metadata
    metadata_file = Path("data/metadata/stocks_metadata.json")
    
    if not metadata_file.exists():
        print("Error: stocks_metadata.json not found")
        return
    
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    # Get NIFTY 50 stocks
    nifty50_symbols = [symbol for symbol, data in metadata.items() 
                       if 'NIFTY 50' in data.get('INDICES', '')]
    
    print(f"\nAnalyzing {len(nifty50_symbols)} NIFTY 50 stocks...")
    
    # Filter for uptrend
    trend_filter = TrendFilter()
    uptrend_stocks = trend_filter.filter_by_trend(
        symbols=nifty50_symbols[:20],  # Analyze first 20 for demo
        trend_type=TrendType.UPTREND,
        period=20,
        min_strength=0.5
    )
    
    print(f"\nFound {len(uptrend_stocks)} stocks in UPTREND:\n")
    
    for stock in uptrend_stocks:
        print(f"{stock['symbol']:15} | Strength: {stock['strength']:6} | "
              f"R²: {stock['r_squared']:.3f} | Change: {stock['price_change_pct']:+6.2f}% | "
              f"Price: ₹{stock['current_price']:.2f}")


def example_3_filter_downtrend_stocks():
    """Example 3: Find stocks in downtrend"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Filter Downtrend Stocks")
    print("="*70)
    
    # Sample symbols to analyze
    symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 
               'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK']
    
    trend_filter = TrendFilter()
    downtrend_stocks = trend_filter.filter_by_trend(
        symbols=symbols,
        trend_type=TrendType.DOWNTREND,
        period=30,
        min_strength=0.6
    )
    
    print(f"\nFound {len(downtrend_stocks)} stocks in DOWNTREND:\n")
    
    for stock in downtrend_stocks:
        print(f"{stock['symbol']:15} | Strength: {stock['strength']:6} | "
              f"R²: {stock['r_squared']:.3f} | Change: {stock['price_change_pct']:+6.2f}% | "
              f"Support: ₹{stock['support']:.2f}")


def example_4_filter_sideways_stocks():
    """Example 4: Find stocks in sideways/consolidation"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Filter Sideways/Consolidating Stocks")
    print("="*70)
    
    symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 
               'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK']
    
    trend_filter = TrendFilter()
    sideways_stocks = trend_filter.filter_by_trend(
        symbols=symbols,
        trend_type=TrendType.SIDEWAYS,
        period=20,
        min_strength=0.4
    )
    
    print(f"\nFound {len(sideways_stocks)} stocks in SIDEWAYS trend:\n")
    
    for stock in sideways_stocks:
        range_pct = ((stock['resistance'] - stock['support']) / stock['support'] * 100)
        print(f"{stock['symbol']:15} | Range: ₹{stock['support']:.2f} - ₹{stock['resistance']:.2f} "
              f"({range_pct:.1f}%) | Current: ₹{stock['current_price']:.2f}")


def example_5_get_all_trends():
    """Example 5: Get trend classification for all stocks"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Trend Classification Summary")
    print("="*70)
    
    symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 
               'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK']
    
    trend_filter = TrendFilter()
    trends_df = trend_filter.get_all_trends(symbols, period=20)
    
    if len(trends_df) == 0:
        print("No data available")
        return
    
    # Group by trend
    print("\nTrend Distribution:")
    trend_counts = trends_df['trend'].value_counts()
    for trend, count in trend_counts.items():
        print(f"  {trend.upper():12} : {count} stocks")
    
    print("\n\nDetailed Results:")
    print(trends_df.to_string(index=False))
    
    # Show strongest uptrend
    uptrends = trends_df[trends_df['trend'] == 'uptrend'].sort_values('r_squared', ascending=False)
    if len(uptrends) > 0:
        best = uptrends.iloc[0]
        print(f"\n🔥 Strongest Uptrend: {best['symbol']} (R²: {best['r_squared']:.3f}, Change: {best['price_change_pct']:+.2f}%)")
    
    # Show strongest downtrend
    downtrends = trends_df[trends_df['trend'] == 'downtrend'].sort_values('r_squared', ascending=False)
    if len(downtrends) > 0:
        worst = downtrends.iloc[0]
        print(f"📉 Strongest Downtrend: {worst['symbol']} (R²: {worst['r_squared']:.3f}, Change: {worst['price_change_pct']:+.2f}%)")


def example_6_filter_by_index():
    """Example 6: Filter uptrend stocks from specific index"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Filter Uptrend Stocks from NIFTY SMALLCAP 100")
    print("="*70)
    
    metadata_file = Path("data/metadata/stocks_metadata.json")
    
    if not metadata_file.exists():
        print("Error: stocks_metadata.json not found")
        return
    
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    # Get NIFTY SMALLCAP 100 stocks
    smallcap_symbols = [symbol for symbol, data in metadata.items() 
                        if 'NIFTY SMALLCAP 100' in data.get('INDICES', '')]
    
    print(f"\nAnalyzing {len(smallcap_symbols)} NIFTY SMALLCAP 100 stocks...")
    
    trend_filter = TrendFilter()
    uptrend_stocks = trend_filter.filter_by_trend(
        symbols=smallcap_symbols[:30],  # First 30 for demo
        trend_type=TrendType.UPTREND,
        period=30,
        min_strength=0.6
    )
    
    print(f"\nFound {len(uptrend_stocks)} strong uptrend stocks:\n")
    
    for i, stock in enumerate(uptrend_stocks[:10], 1):
        print(f"{i:2}. {stock['symbol']:15} | R²: {stock['r_squared']:.3f} | "
              f"Change: {stock['price_change_pct']:+6.2f}% | "
              f"Resistance: ₹{stock['resistance']:.2f}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TREND-BASED STOCK FILTERING EXAMPLES")
    print("="*70)
    
    # Run examples
    example_1_detect_single_stock()
    example_2_filter_uptrend_stocks()
    example_3_filter_downtrend_stocks()
    example_4_filter_sideways_stocks()
    example_5_get_all_trends()
    example_6_filter_by_index()
    
    print("\n" + "="*70)
    print("Examples completed!")
    print("="*70 + "\n")
