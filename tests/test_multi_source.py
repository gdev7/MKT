"""
Test script for multi-source data fetcher.

This script tests the multi-source data fetcher with various scenarios.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from src.data_fetch.multi_source_fetcher import MultiSourceFetcher
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_multi_source_fetcher():
    """Test multi-source fetcher with various symbols."""
    
    print("\n" + "="*60)
    print("MULTI-SOURCE DATA FETCHER TEST")
    print("="*60)
    
    # Initialize fetcher
    fetcher = MultiSourceFetcher()
    
    print(f"\nAvailable sources: {fetcher.get_available_sources()}")
    print()
    
    # Test symbols
    test_symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK"]
    
    # Date range (last 30 days)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    print(f"Fetching data from {start_date} to {end_date}")
    print()
    
    results = {}
    
    for symbol in test_symbols:
        print(f"\n{'='*60}")
        print(f"Testing: {symbol}")
        print(f"{'='*60}")
        
        try:
            data = fetcher.fetch(symbol, start_date, end_date)
            
            if data is not None and not data.empty:
                results[symbol] = {
                    'success': True,
                    'records': len(data),
                    'source': data['Source'].iloc[0] if 'Source' in data.columns else 'Unknown',
                    'date_range': f"{data['Date'].min()} to {data['Date'].max()}"
                }
                print(f"✓ Success!")
                print(f"  Records: {len(data)}")
                print(f"  Source: {results[symbol]['source']}")
                print(f"  Date range: {results[symbol]['date_range']}")
                print(f"\nFirst few rows:")
                print(data.head())
            else:
                results[symbol] = {'success': False, 'error': 'No data returned'}
                print(f"✗ Failed: No data returned")
                
        except Exception as e:
            results[symbol] = {'success': False, 'error': str(e)}
            print(f"✗ Failed: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    successful = sum(1 for r in results.values() if r['success'])
    total = len(results)
    
    print(f"\nTests passed: {successful}/{total}")
    print()
    
    for symbol, result in results.items():
        if result['success']:
            print(f"✓ {symbol:12} - {result['records']:4} records from {result['source']}")
        else:
            print(f"✗ {symbol:12} - {result['error']}")
    
    print()


def test_source_availability():
    """Test individual source availability."""
    
    print("\n" + "="*60)
    print("SOURCE AVAILABILITY TEST")
    print("="*60)
    print()
    
    from src.data_fetch.nsepython_source import NSEPythonSource
    from src.data_fetch.yfinance_source import YFinanceSource
    from src.data_fetch.nse_official_source import NSEOfficialSource
    
    sources = [
        NSEPythonSource(),
        NSEOfficialSource(),
        YFinanceSource(),
    ]
    
    for source in sources:
        status = "✓ Available" if source.is_available() else "✗ Not Available"
        print(f"{source.name:20} - {status}")
    
    print()


if __name__ == "__main__":
    # Test source availability
    test_source_availability()
    
    # Test multi-source fetcher
    test_multi_source_fetcher()
