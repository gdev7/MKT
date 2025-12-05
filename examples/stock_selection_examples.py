"""
Stock Selection Examples - Demonstrates various ways to select stocks for backtesting.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.stock_selector import StockSelector


def example_1_list_available_options():
    """Example 1: See what's available."""
    print("\n" + "="*70)
    print("EXAMPLE 1: List Available Options")
    print("="*70)
    
    selector = StockSelector()
    
    # List available indices
    print("\nTop 10 Indices by Stock Count:")
    print("-"*70)
    indices = selector.list_available_indices()
    for idx_name, count in list(indices.items())[:10]:
        print(f"{idx_name:45} {count:4} stocks")
    
    # List available sectors
    print("\nTop 10 Sectors by Stock Count:")
    print("-"*70)
    sectors = selector.list_available_sectors()
    for sector_name, count in list(sectors.items())[:10]:
        print(f"{sector_name:45} {count:4} stocks")
    
    # List available industries
    print("\nTop 10 Industries by Stock Count:")
    print("-"*70)
    industries = selector.list_available_industries()
    for industry_name, count in list(industries.items())[:10]:
        print(f"{industry_name:45} {count:4} stocks")


def example_2_select_by_index():
    """Example 2: Select stocks from specific indices."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Select by Index")
    print("="*70)
    
    selector = StockSelector()
    
    # NIFTY 50
    nifty50 = selector.get_by_index('NIFTY 50')
    print(f"\nNIFTY 50: {len(nifty50)} stocks")
    print(f"Sample: {', '.join(nifty50[:10])}")
    
    # NIFTY 100
    nifty100 = selector.get_by_index('NIFTY 100')
    print(f"\nNIFTY 100: {len(nifty100)} stocks")
    print(f"Sample: {', '.join(nifty100[:10])}")
    
    # NIFTY MIDCAP 100
    midcap = selector.get_by_index('NIFTY MIDCAP 100')
    print(f"\nNIFTY MIDCAP 100: {len(midcap)} stocks")
    print(f"Sample: {', '.join(midcap[:10])}")
    
    # NIFTY SMALLCAP 100
    smallcap = selector.get_by_index('NIFTY SMALLCAP 100')
    print(f"\nNIFTY SMALLCAP 100: {len(smallcap)} stocks")
    print(f"Sample: {', '.join(smallcap[:10])}")


def example_3_select_by_sector():
    """Example 3: Select stocks from specific sectors."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Select by Sector")
    print("="*70)
    
    selector = StockSelector()
    
    # IT Sector
    it_stocks = selector.get_by_sector('IT')
    print(f"\nIT Sector: {len(it_stocks)} stocks")
    if it_stocks:
        print(f"Sample: {', '.join(it_stocks[:10])}")
    
    # Banking
    bank_stocks = selector.get_by_sector('Banking')
    print(f"\nBanking Sector: {len(bank_stocks)} stocks")
    if bank_stocks:
        print(f"Sample: {', '.join(bank_stocks[:10])}")
    
    # Pharma
    pharma_stocks = selector.get_by_sector('Pharma')
    print(f"\nPharma Sector: {len(pharma_stocks)} stocks")
    if pharma_stocks:
        print(f"Sample: {', '.join(pharma_stocks[:10])}")


def example_4_select_single_or_custom():
    """Example 4: Single stock or custom list."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Single Stock or Custom List")
    print("="*70)
    
    selector = StockSelector()
    
    # Single stock
    single = selector.get_single_stock('RELIANCE')
    print(f"\nSingle Stock: {single}")
    
    # Custom list
    my_stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']
    custom = selector.get_by_custom_list(my_stocks)
    print(f"\nCustom List: {custom}")
    
    # Custom list with some invalid symbols
    mixed_list = ['RELIANCE', 'INVALID123', 'TCS', 'BADSTOCK', 'INFY']
    filtered = selector.get_by_custom_list(mixed_list)
    print(f"\nFiltered List: {filtered}")


def example_5_flexible_selection():
    """Example 5: Using flexible get_by_criteria()."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Flexible Selection with get_by_criteria()")
    print("="*70)
    
    selector = StockSelector()
    
    # All stocks
    all_stocks = selector.get_by_criteria(selection_type='all')
    print(f"\nAll stocks: {len(all_stocks)}")
    
    # Single stock
    single = selector.get_by_criteria(selection_type='single', value='TCS')
    print(f"\nSingle stock: {single}")
    
    # Index
    nifty50 = selector.get_by_criteria(selection_type='index', value='NIFTY 50')
    print(f"\nNIFTY 50: {len(nifty50)} stocks")
    
    # Sector
    it_stocks = selector.get_by_criteria(selection_type='sector', value='IT')
    print(f"\nIT Sector: {len(it_stocks)} stocks")
    
    # Custom
    custom_list = ['RELIANCE', 'TCS', 'INFY']
    custom = selector.get_by_criteria(selection_type='custom', custom_list=custom_list)
    print(f"\nCustom list: {custom}")


def example_6_stock_info():
    """Example 6: Get detailed stock information."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Get Stock Details")
    print("="*70)
    
    selector = StockSelector()
    
    stocks = ['RELIANCE', 'TCS', 'INFY']
    
    for symbol in stocks:
        info = selector.get_stock_info(symbol)
        print(f"\n{symbol}:")
        print(f"  Name: {info.get('NAME OF COMPANY', 'N/A')}")
        print(f"  Sector: {info.get('SECTOR', 'N/A')}")
        print(f"  Industry: {info.get('INDUSTRY', 'N/A')}")
        indices = info.get('INDICES', [])
        if indices:
            print(f"  Indices: {len(indices)} ({', '.join(indices[:3])}...)")
        else:
            print(f"  Indices: None")


def example_7_filter_by_data():
    """Example 7: Filter by data availability."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Filter by Data Availability")
    print("="*70)
    
    selector = StockSelector()
    
    # Get NIFTY 50
    nifty50 = selector.get_by_index('NIFTY 50')
    print(f"\nNIFTY 50: {len(nifty50)} stocks")
    
    # Filter to stocks with at least 1 year of data
    with_data = selector.filter_by_data_availability(nifty50, min_days=252)
    print(f"With 1+ year data: {len(with_data)} stocks")
    
    # Filter to stocks with at least 3 years of data
    with_3y_data = selector.filter_by_data_availability(nifty50, min_days=252*3)
    print(f"With 3+ years data: {len(with_3y_data)} stocks")


if __name__ == "__main__":
    print("="*70)
    print("STOCK SELECTION EXAMPLES")
    print("="*70)
    
    example_1_list_available_options()
    example_2_select_by_index()
    example_3_select_by_sector()
    example_4_select_single_or_custom()
    example_5_flexible_selection()
    example_6_stock_info()
    example_7_filter_by_data()
    
    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70)
