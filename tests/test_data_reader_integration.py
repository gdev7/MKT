"""
Test DataReader integration with existing code

Verifies that DataReader works correctly with:
- TrendDetector/TrendFilter
- BaseAnalyzer and subclasses
- StockSelector
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.data_reader import DataReader
from src.analysis.trend_detector import TrendDetector, TrendFilter, TrendType
from src.utils.stock_selector import StockSelector, load_stock_data


def test_data_reader_basic():
    """Test basic DataReader functionality"""
    print("\n" + "="*70)
    print("TEST 1: DataReader Basic Functionality")
    print("="*70)
    
    reader = DataReader()
    
    # Test price data loading
    df = reader.get_price_data('HDFCBANK')
    assert df is not None, "Failed to load price data"
    assert len(df) > 0, "Price data is empty"
    assert 'close' in df.columns, "Missing close column"
    print(f"✓ Price data loaded: {len(df)} records")
    
    # Test metadata loading
    metadata = reader.get_stock_metadata('HDFCBANK')
    assert metadata is not None, "Failed to load metadata"
    print(f"✓ Metadata loaded: {metadata.get('NAME OF COMPANY')}")
    
    # Test index filtering
    nifty50 = reader.get_stocks_by_index('NIFTY 50')
    assert len(nifty50) > 0, "Failed to get NIFTY 50 stocks"
    print(f"✓ Index filtering: {len(nifty50)} NIFTY 50 stocks")
    
    print("\n✅ DataReader basic tests passed!")


def test_trend_detector_integration():
    """Test TrendDetector with DataReader"""
    print("\n" + "="*70)
    print("TEST 2: TrendDetector Integration")
    print("="*70)
    
    reader = DataReader()
    trend_filter = TrendFilter(data_reader=reader)
    
    # Test single stock trend detection
    df = reader.get_price_data('RELIANCE')
    assert df is not None, "Failed to load price data"
    
    detector = TrendDetector()
    result = detector.detect_trend_with_strength(df, period=20)
    
    assert 'trend' in result, "Missing trend in result"
    assert 'r_squared' in result, "Missing r_squared in result"
    print(f"✓ Trend detected: {result['trend'].value}")
    print(f"✓ R-squared: {result['r_squared']:.3f}")
    
    # Test batch filtering
    symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY']
    trends = trend_filter.get_all_trends(symbols, period=20)
    
    assert len(trends) > 0, "Failed to get trends"
    print(f"✓ Batch trends: {len(trends)} stocks analyzed")
    
    print("\n✅ TrendDetector integration tests passed!")


def test_stock_selector_integration():
    """Test StockSelector with DataReader"""
    print("\n" + "="*70)
    print("TEST 3: StockSelector Integration")
    print("="*70)
    
    selector = StockSelector()
    
    # Test index selection
    nifty50 = selector.get_by_index('NIFTY 50')
    assert len(nifty50) > 0, "Failed to select NIFTY 50"
    print(f"✓ Index selection: {len(nifty50)} stocks")
    
    # Test data loading
    symbols = nifty50[:5]  # First 5 stocks
    data = load_stock_data(symbols)
    
    assert len(data) > 0, "Failed to load stock data"
    print(f"✓ Data loading: {len(data)} stocks loaded")
    
    for symbol, df in data.items():
        assert len(df) > 0, f"Empty data for {symbol}"
        assert 'close' in df.columns, f"Missing close column for {symbol}"
    
    print("\n✅ StockSelector integration tests passed!")


def test_combined_workflow():
    """Test complete workflow using DataReader"""
    print("\n" + "="*70)
    print("TEST 4: Combined Workflow")
    print("="*70)
    
    # Step 1: Select stocks
    reader = DataReader()
    nifty50 = reader.get_stocks_by_index('NIFTY 50')
    print(f"✓ Selected {len(nifty50)} NIFTY 50 stocks")
    
    # Step 2: Filter by market cap
    large_caps = [s for s in nifty50 
                  if s in reader.get_stocks_by_market_cap(min_cap=50000)]
    print(f"✓ Filtered to {len(large_caps)} large caps")
    
    # Step 3: Analyze trends
    trend_filter = TrendFilter(data_reader=reader)
    trends_df = trend_filter.get_all_trends(large_caps[:10], period=20)
    print(f"✓ Analyzed trends for {len(trends_df)} stocks")
    
    # Step 4: Get complete data
    if len(trends_df) > 0:
        for i, row in trends_df.head(3).iterrows():
            symbol = row['symbol']
            data = reader.get_stock_complete(symbol, days=30)
            assert data is not None, f"Failed to get complete data for {symbol}"
            assert 'metadata' in data, f"Missing metadata for {symbol}"
            if data.get('price_stats'):
                print(f"✓ Complete data for {symbol}: {data['price_stats']['change_pct']:+.2f}%")
            else:
                print(f"✓ Complete data for {symbol}: (no price data)")
    else:
        print(f"✓ No stocks analyzed (insufficient data)")
    
    print("\n✅ Combined workflow tests passed!")


def test_performance():
    """Test DataReader caching performance"""
    print("\n" + "="*70)
    print("TEST 5: Performance & Caching")
    print("="*70)
    
    import time
    
    reader = DataReader()
    
    # First load (from file)
    start = time.time()
    metadata1 = reader.get_all_metadata()
    time1 = time.time() - start
    print(f"✓ First metadata load: {time1:.4f}s ({len(metadata1)} stocks)")
    
    # Second load (from cache)
    start = time.time()
    metadata2 = reader.get_all_metadata()
    time2 = time.time() - start
    print(f"✓ Cached metadata load: {time2:.4f}s (speedup: {time1/time2:.1f}x)")
    
    assert metadata1 == metadata2, "Cache returned different data"
    assert time2 < time1, "Cache is not faster"
    
    # Batch loading
    symbols = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK']
    
    start = time.time()
    data = reader.get_multiple_stocks(symbols, include_prices=True, days=30)
    batch_time = time.time() - start
    print(f"✓ Batch load ({len(symbols)} stocks): {batch_time:.4f}s")
    
    assert len(data) == len(symbols), "Not all stocks loaded"
    
    print("\n✅ Performance tests passed!")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("DATA READER INTEGRATION TESTS")
    print("="*70)
    
    try:
        test_data_reader_basic()
        test_trend_detector_integration()
        test_stock_selector_integration()
        test_combined_workflow()
        test_performance()
        
        print("\n" + "="*70)
        print("ALL TESTS PASSED! ✅")
        print("="*70 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        raise
