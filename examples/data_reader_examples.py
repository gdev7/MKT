"""
Data Reader Examples - Complete usage guide

Demonstrates all capabilities of the DataReader class:
1. Loading price data
2. Accessing metadata
3. Filtering stocks by various criteria
4. Combining data sources
5. Searching and querying
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.data_reader import DataReader


def example_1_basic_usage():
    """Example 1: Basic data loading"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Data Loading")
    print("="*70)
    
    reader = DataReader()
    
    # Load price data
    print("\n1. Loading price data for HDFCBANK...")
    df = reader.get_price_data('HDFCBANK')
    if df is not None:
        print(f"   Loaded {len(df)} days of data")
        print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"   Latest price: ₹{df.iloc[-1]['close']:.2f}")
    
    # Get latest price
    print("\n2. Getting latest price...")
    price = reader.get_latest_price('RELIANCE')
    if price:
        print(f"   RELIANCE latest: ₹{price:.2f}")
    
    # Get metadata
    print("\n3. Loading metadata for TCS...")
    metadata = reader.get_stock_metadata('TCS')
    if metadata:
        print(f"   Name: {metadata.get('NAME OF COMPANY')}")
        print(f"   Sector: {metadata.get('SECTOR')}")
        print(f"   Market Cap: {metadata.get('MARKET_CAP')} Cr")


def example_2_price_analysis():
    """Example 2: Price data analysis"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Price Data Analysis")
    print("="*70)
    
    reader = DataReader()
    
    symbols = ['HDFCBANK', 'ICICIBANK', 'SBIN']
    
    print("\n30-day price statistics:")
    print("-" * 70)
    
    for symbol in symbols:
        stats = reader.get_price_range(symbol, days=30)
        if stats:
            print(f"\n{symbol}:")
            print(f"  Current: ₹{stats['current']:.2f}")
            print(f"  30-day High: ₹{stats['high']:.2f}")
            print(f"  30-day Low: ₹{stats['low']:.2f}")
            print(f"  Average: ₹{stats['avg']:.2f}")
            print(f"  Change: {stats['change_pct']:+.2f}%")


def example_3_filter_by_index():
    """Example 3: Filter stocks by index membership"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Filter by Index")
    print("="*70)
    
    reader = DataReader()
    
    # Get NIFTY 50 stocks
    print("\n1. NIFTY 50 stocks...")
    nifty50 = reader.get_stocks_by_index('NIFTY 50')
    print(f"   Found {len(nifty50)} stocks")
    print(f"   Examples: {', '.join(nifty50[:5])}")
    
    # Get NIFTY SMALLCAP 100 stocks
    print("\n2. NIFTY SMALLCAP 100 stocks...")
    smallcap = reader.get_stocks_by_index('NIFTY SMALLCAP 100')
    print(f"   Found {len(smallcap)} stocks")
    print(f"   Examples: {', '.join(smallcap[:5])}")
    
    # Get NIFTY BANK stocks
    print("\n3. NIFTY BANK stocks...")
    bank = reader.get_stocks_by_index('NIFTY BANK')
    print(f"   Found {len(bank)} stocks")
    print(f"   All: {', '.join(bank)}")


def example_4_filter_by_sector():
    """Example 4: Filter stocks by sector"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Filter by Sector")
    print("="*70)
    
    reader = DataReader()
    
    # Get IT sector stocks
    print("\n1. IT Sector stocks...")
    it_stocks = reader.get_stocks_by_sector('IT', level='SECTOR_GROUP')
    print(f"   Found {len(it_stocks)} stocks")
    print(f"   Examples: {', '.join(it_stocks[:10])}")
    
    # Get Pharma stocks
    print("\n2. Pharmaceutical stocks...")
    pharma_stocks = reader.get_stocks_by_sector('Pharma', level='SECTOR_GROUP')
    print(f"   Found {len(pharma_stocks)} stocks")
    print(f"   Examples: {', '.join(pharma_stocks[:10])}")
    
    # Get Banking stocks
    print("\n3. Banking sector stocks...")
    banking = reader.get_stocks_by_sector('Banking', level='SECTOR_GROUP')
    print(f"   Found {len(banking)} stocks")
    print(f"   Examples: {', '.join(banking[:10])}")


def example_5_filter_by_market_cap():
    """Example 5: Filter by market cap"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Filter by Market Cap")
    print("="*70)
    
    reader = DataReader()
    
    # Large caps (> 1 lakh crore)
    print("\n1. Large caps (> ₹1,00,000 Cr)...")
    large_caps = reader.get_stocks_by_market_cap(min_cap=100000)
    print(f"   Found {len(large_caps)} stocks")
    print(f"   Examples: {', '.join(large_caps[:10])}")
    
    # Mid caps (10,000 to 100,000 crore)
    print("\n2. Mid caps (₹10,000 - ₹1,00,000 Cr)...")
    mid_caps = reader.get_stocks_by_market_cap(min_cap=10000, max_cap=100000)
    print(f"   Found {len(mid_caps)} stocks")
    print(f"   Examples: {', '.join(mid_caps[:10])}")
    
    # Small caps (< 10,000 crore)
    print("\n3. Small caps (< ₹10,000 Cr)...")
    small_caps = reader.get_stocks_by_market_cap(max_cap=10000)
    print(f"   Found {len(small_caps)} stocks")
    print(f"   Examples: {', '.join(small_caps[:10])}")


def example_6_combined_filters():
    """Example 6: Combine multiple filters"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Combined Filters")
    print("="*70)
    
    reader = DataReader()
    
    # Get large-cap IT stocks in NIFTY 50
    print("\n1. Large-cap IT stocks in NIFTY 50...")
    
    nifty50 = set(reader.get_stocks_by_index('NIFTY 50'))
    it_stocks = set(reader.get_stocks_by_sector('IT', level='SECTOR_GROUP'))
    large_caps = set(reader.get_stocks_by_market_cap(min_cap=50000))
    
    result = nifty50 & it_stocks & large_caps
    print(f"   Found {len(result)} stocks: {', '.join(sorted(result))}")
    
    # Get mid-cap pharma stocks
    print("\n2. Mid-cap Pharmaceutical stocks...")
    
    pharma = set(reader.get_stocks_by_sector('Pharma', level='SECTOR_GROUP'))
    mid_caps = set(reader.get_stocks_by_market_cap(min_cap=10000, max_cap=100000))
    
    result = pharma & mid_caps
    print(f"   Found {len(result)} stocks")
    print(f"   Examples: {', '.join(sorted(list(result))[:10])}")


def example_7_complete_stock_data():
    """Example 7: Get complete stock information"""
    print("\n" + "="*70)
    print("EXAMPLE 7: Complete Stock Data")
    print("="*70)
    
    reader = DataReader()
    
    symbol = "INFY"
    print(f"\nGetting complete data for {symbol}...")
    
    data = reader.get_stock_complete(symbol, days=90)
    
    if data:
        metadata = data['metadata']
        price_stats = data['price_stats']
        price_data = data['price_data']
        
        print(f"\nMetadata:")
        print(f"  Name: {metadata.get('NAME OF COMPANY')}")
        print(f"  Sector: {metadata.get('SECTOR')}")
        print(f"  Market Cap: {metadata.get('MARKET_CAP')} Cr")
        print(f"  PE Ratio: {metadata.get('PE_RATIO')}")
        print(f"  ROE: {metadata.get('ROE')}%")
        
        if price_stats:
            print(f"\nPrice (90 days):")
            print(f"  Current: ₹{price_stats['current']:.2f}")
            print(f"  High: ₹{price_stats['high']:.2f}")
            print(f"  Low: ₹{price_stats['low']:.2f}")
            print(f"  Change: {price_stats['change_pct']:+.2f}%")
        
        if price_data is not None:
            print(f"\nPrice data loaded: {len(price_data)} days")


def example_8_search_stocks():
    """Example 8: Search for stocks"""
    print("\n" + "="*70)
    print("EXAMPLE 8: Search Stocks")
    print("="*70)
    
    reader = DataReader()
    
    # Search by symbol
    print("\n1. Search for 'HDFC'...")
    results = reader.search_stocks('HDFC')
    print(f"   Found {len(results)} stocks")
    print(f"   Results: {', '.join(results[:10])}")
    
    # Search by name
    print("\n2. Search for 'BANK'...")
    results = reader.search_stocks('BANK')
    print(f"   Found {len(results)} stocks")
    print(f"   Examples: {', '.join(results[:10])}")
    
    # Search for specific company
    print("\n3. Search for 'INFOSYS'...")
    results = reader.search_stocks('INFOSYS')
    print(f"   Found {len(results)} stocks: {', '.join(results)}")


def example_9_multiple_stocks():
    """Example 9: Load multiple stocks efficiently"""
    print("\n" + "="*70)
    print("EXAMPLE 9: Load Multiple Stocks")
    print("="*70)
    
    reader = DataReader()
    
    # Get top NIFTY 50 stocks
    symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK']
    
    print(f"\nLoading data for {len(symbols)} stocks...")
    
    # Without price data
    print("\n1. Metadata only...")
    data = reader.get_multiple_stocks(symbols, include_prices=False)
    print(f"   Loaded {len(data)} stocks")
    for symbol, stock_data in list(data.items())[:3]:
        metadata = stock_data['metadata']
        print(f"   {symbol}: {metadata.get('NAME OF COMPANY')}")
    
    # With price data
    print("\n2. With 30-day price data...")
    data = reader.get_multiple_stocks(symbols, include_prices=True, days=30)
    print(f"   Loaded {len(data)} stocks with price data")
    for symbol, stock_data in list(data.items())[:3]:
        stats = stock_data['price_stats']
        if stats:
            print(f"   {symbol}: ₹{stats['current']:.2f} ({stats['change_pct']:+.2f}%)")


def example_10_summary_stats():
    """Example 10: Get data summary"""
    print("\n" + "="*70)
    print("EXAMPLE 10: Data Summary")
    print("="*70)
    
    reader = DataReader()
    
    stats = reader.get_summary_stats()
    
    print(f"\nDataset Statistics:")
    print(f"  Total stocks in metadata: {stats['total_stocks_in_metadata']}")
    print(f"  Stocks with price data: {stats['stocks_with_price_data']}")
    print(f"  Enriched stocks: {stats['enriched_stocks']}")
    print(f"  Number of indices: {stats['index_count']}")
    
    print(f"\nAvailable indices:")
    for idx in stats['available_indices'][:10]:
        count = len(reader.get_stocks_by_index(idx))
        print(f"  {idx}: {count} stocks")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("DATA READER - USAGE EXAMPLES")
    print("="*70)
    
    # Run all examples
    example_1_basic_usage()
    example_2_price_analysis()
    example_3_filter_by_index()
    example_4_filter_by_sector()
    example_5_filter_by_market_cap()
    example_6_combined_filters()
    example_7_complete_stock_data()
    example_8_search_stocks()
    example_9_multiple_stocks()
    example_10_summary_stats()
    
    print("\n" + "="*70)
    print("All examples completed successfully!")
    print("="*70 + "\n")
