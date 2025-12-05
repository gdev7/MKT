"""
Example: Using the Multi-Source Data Fetcher

This demonstrates how to use the enhanced DataFetcher with multi-source support.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_fetch.data_fetcher import DataFetcher
from src.utils.logger import get_logger

logger = get_logger(__name__)


def example_basic_usage():
    """Basic usage with automatic multi-source fallback."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Multi-Source Usage")
    print("="*60 + "\n")
    
    # Initialize with multi-source enabled (default)
    fetcher = DataFetcher(use_multi_source=True)
    
    # Fetch 5 years of data for RELIANCE
    print("Fetching 5 years of RELIANCE data...")
    data = fetcher.fetch_all("RELIANCE", years=5)
    
    if data is not None:
        print(f"\n✓ Success! Retrieved {len(data)} records")
        if 'Source' in data.columns:
            print(f"  Data source: {data['Source'].iloc[0]}")
        print(f"  Date range: {data['Date'].min()} to {data['Date'].max()}")
        print(f"\nFirst 5 rows:")
        print(data.head())
    else:
        print("✗ Failed to fetch data")


def example_legacy_mode():
    """Using legacy mode (yfinance only)."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Legacy Mode (YFinance only)")
    print("="*60 + "\n")
    
    # Use yfinance only
    fetcher = DataFetcher(use_multi_source=False)
    
    print("Fetching TCS data (yfinance only)...")
    data = fetcher.fetch_all("TCS", years=2)
    
    if data is not None:
        print(f"\n✓ Success! Retrieved {len(data)} records")
        print(f"  Date range: {data['Date'].min()} to {data['Date'].max()}")


def example_incremental_update():
    """Incremental update of existing data."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Incremental Update")
    print("="*60 + "\n")
    
    fetcher = DataFetcher(use_multi_source=True)
    
    # First, ensure we have some historical data
    print("Step 1: Fetching initial data for INFY...")
    data = fetcher.fetch_all("INFY", years=1)
    
    if data is not None:
        print(f"✓ Initial data: {len(data)} records")
        
        # Now update with latest data
        print("\nStep 2: Updating with latest data...")
        updated = fetcher.fetch_latest("INFY")
        
        if updated is not None:
            print(f"✓ Updated data: {len(updated)} records")
        else:
            print("Already up-to-date!")


def example_multiple_stocks():
    """Fetch data for multiple stocks."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Multiple Stocks")
    print("="*60 + "\n")
    
    fetcher = DataFetcher(use_multi_source=True, delay=1.0)
    
    stocks = ["RELIANCE", "TCS", "INFY"]
    
    print(f"Fetching data for {len(stocks)} stocks...\n")
    
    results = {}
    for symbol in stocks:
        print(f"Fetching {symbol}...")
        data = fetcher.fetch_all(symbol, years=1)
        
        if data is not None:
            source = data['Source'].iloc[0] if 'Source' in data.columns else 'Unknown'
            results[symbol] = {
                'records': len(data),
                'source': source,
                'latest': data['Date'].max()
            }
            print(f"  ✓ {len(data)} records from {source}")
        else:
            print(f"  ✗ Failed")
    
    print(f"\nSummary:")
    print("-" * 60)
    for symbol, info in results.items():
        print(f"{symbol:12} - {info['records']:5} records from {info['source']:15} (latest: {info['latest']})")


def example_check_sources():
    """Check which sources are available."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Check Available Sources")
    print("="*60 + "\n")
    
    from src.data_fetch.multi_source_fetcher import MultiSourceFetcher
    
    fetcher = MultiSourceFetcher()
    
    available = fetcher.get_available_sources()
    print(f"Available data sources: {', '.join(available)}")
    
    for source_name in ['NSEPython', 'YFinance', 'NSE Official']:
        source = fetcher.get_source_by_name(source_name)
        if source:
            status = "✓ Available" if source.is_available() else "✗ Not Available"
            print(f"  {source_name:15} - {status}")


if __name__ == "__main__":
    # Run all examples
    example_check_sources()
    example_basic_usage()
    example_legacy_mode()
    example_incremental_update()
    example_multiple_stocks()
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)
