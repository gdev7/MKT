"""
Example Usage of Stock Data Reader and Analyzer

This script demonstrates all the features of the StockDataReader and StockDataAnalyzer classes.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_fetch.stock_data_reader import StockDataReader
from src.data_fetch.stock_data_analyzer import StockDataAnalyzer


def main():
    """Demonstrate all features of the stock data access system."""
    
    # Initialize reader with a stock CSV file
    csv_path = Path(__file__).parent.parent / 'data' / 'raw' / '3MINDIA.csv'
    reader = StockDataReader(csv_path)
    
    print("=" * 80)
    print("STOCK DATA READER - EXAMPLES")
    print("=" * 80)
    
    # 1. Get stock information
    print("\n1. Stock Information:")
    print(reader)
    info = reader.get_info()
    print(f"   Symbol: {info['symbol']}")
    print(f"   Total Records: {info['total_records']}")
    print(f"   Date Range: {info['date_range']['start']} to {info['date_range']['end']}")
    print(f"   Years Available: {info['years_available']}")
    
    # 2. Get complete data (all columns)
    print("\n2. Get Complete Data (first 5 rows):")
    all_data = reader.get_columns()
    print(all_data.head())
    
    # 3. Get specific columns
    print("\n3. Get Specific Columns (Date, Close, Volume):")
    price_data = reader.get_columns(['Date', 'Close', 'Volume'])
    print(price_data.head())
    
    # 4. Get data for a date range
    print("\n4. Get Data for Date Range (2024-01-01 to 2024-12-31):")
    range_data = reader.get_date_range('2024-01-01', '2024-12-31')
    print(f"   Records found: {len(range_data)}")
    if len(range_data) > 0:
        print(range_data.head())
    
    # 5. Get data from a particular date onwards
    print("\n5. Get Data from 2024-01-01 onwards:")
    from_date_data = reader.get_from_date('2024-01-01')
    print(f"   Records found: {len(from_date_data)}")
    if len(from_date_data) > 0:
        print(from_date_data.head())
    
    # 6. Get data for a specific date
    print("\n6. Get Data for Specific Date (2024-01-15):")
    try:
        specific_date = reader.get_on_date('2024-01-15')
        print(specific_date)
    except Exception as e:
        print(f"   Note: {e}")
    
    # 7. Get lookback data (date + previous N days)
    print("\n7. Get Lookback Data (10 trading days before 2024-01-31):")
    try:
        lookback_data = reader.get_lookback('2024-01-31', days=10)
        print(f"   Records found: {len(lookback_data)}")
        print(lookback_data[['Date', 'Close']])
    except Exception as e:
        print(f"   Note: {e}")
    
    # 8. Get data by year
    print("\n8. Get Data by Year (2024):")
    year_data = reader.get_by_year(2024)
    print(f"   Records found: {len(year_data)}")
    if len(year_data) > 0:
        print(year_data.head())
    
    # 9. Get data by quarter
    print("\n9. Get Data by Quarter (Q1 2024):")
    try:
        q1_data = reader.get_by_quarter(2024, 1)
        print(f"   Records found: {len(q1_data)}")
        if len(q1_data) > 0:
            print(q1_data.head())
    except Exception as e:
        print(f"   Note: {e}")
    
    # 10. Get data by month
    print("\n10. Get Data by Month (January 2024):")
    try:
        jan_data = reader.get_by_month(2024, 1)
        print(f"   Records found: {len(jan_data)}")
        if len(jan_data) > 0:
            print(jan_data.head())
    except Exception as e:
        print(f"   Note: {e}")
    
    # 11. Get data by week
    print("\n11. Get Data by Week (Week 1 of 2024):")
    try:
        week_data = reader.get_by_week(2024, 1)
        print(f"   Records found: {len(week_data)}")
        if len(week_data) > 0:
            print(week_data)
    except Exception as e:
        print(f"   Note: {e}")
    
    print("\n" + "=" * 80)
    print("STOCK DATA ANALYZER - EXAMPLES")
    print("=" * 80)
    
    # Get some data for analysis (last 100 records)
    analysis_data = reader.get_columns().tail(100)
    analyzer = StockDataAnalyzer(analysis_data)
    
    print(f"\nAnalyzing last 100 records...")
    print(analyzer)
    
    # 12. Calculate average
    print("\n12. Calculate Average:")
    avg_close = analyzer.average('Close')
    avg_volume = analyzer.average('Volume')
    print(f"   Average Close Price: {avg_close:.2f}")
    print(f"   Average Volume: {avg_volume:.2f}")
    
    # 13. Get maximum value
    print("\n13. Get Maximum Value:")
    max_close = analyzer.max_value('Close')
    print(f"   Max Close: {max_close['value']:.2f} on {max_close['date']}")
    max_volume = analyzer.max_value('Volume')
    print(f"   Max Volume: {max_volume['value']:.0f} on {max_volume['date']}")
    
    # 14. Get minimum value
    print("\n14. Get Minimum Value:")
    min_close = analyzer.min_value('Close')
    print(f"   Min Close: {min_close['value']:.2f} on {min_close['date']}")
    min_volume = analyzer.min_value('Volume')
    print(f"   Min Volume: {min_volume['value']:.0f} on {min_volume['date']}")
    
    # 15. Summary statistics
    print("\n15. Summary Statistics for Close Price:")
    stats = analyzer.summary_stats('Close')
    for key, value in stats.items():
        print(f"   {key}: {value:.2f}")
    
    # 16. Simple Moving Average
    print("\n16. Simple Moving Average (SMA):")
    sma_20 = analyzer.simple_moving_average('Close', window=20)
    print(f"   SMA-20 (last 5 values):")
    print(sma_20.tail())
    
    # 17. Exponential Moving Average
    print("\n17. Exponential Moving Average (EMA):")
    ema_12 = analyzer.exponential_moving_average('Close', span=12)
    print(f"   EMA-12 (last 5 values):")
    print(ema_12.tail())
    
    # 18. Calculate returns
    print("\n18. Calculate Returns:")
    daily_returns = analyzer.returns('Close', periods=1)
    print(f"   Daily Returns (last 5 values):")
    print(daily_returns.tail())
    
    # 19. Calculate volatility
    print("\n19. Calculate Volatility:")
    vol_20 = analyzer.volatility('Close', window=20)
    print(f"   20-day Volatility (last 5 values):")
    print(vol_20.tail())
    
    # 20. Multiple moving averages comparison
    print("\n20. Multiple Moving Averages:")
    sma_10 = analyzer.simple_moving_average('Close', window=10, add_to_data=True)
    sma_20 = analyzer.simple_moving_average('Close', window=20, add_to_data=True)
    sma_50 = analyzer.simple_moving_average('Close', window=50, add_to_data=True)
    
    result_data = analyzer.get_data()
    print(f"   Latest values:")
    latest = result_data.iloc[-1]
    print(f"   Close: {latest['Close']:.2f}")
    print(f"   SMA-10: {latest['SMA_10']:.2f}")
    print(f"   SMA-20: {latest['SMA_20']:.2f}")
    print(f"   SMA-50: {latest['SMA_50']:.2f}")
    
    # 21. Daily range analysis
    print("\n21. Daily Range Analysis:")
    daily_range = analyzer.daily_range()
    print(f"   Average Daily Range: {daily_range.mean():.2f}")
    print(f"   Max Daily Range: {daily_range.max():.2f}")
    print(f"   Min Daily Range: {daily_range.min():.2f}")
    
    # 22. Cumulative returns
    print("\n22. Cumulative Returns:")
    cum_returns = analyzer.cumulative_returns('Close')
    print(f"   Total Return over period: {cum_returns.iloc[-1]:.2f}%")
    
    print("\n" + "=" * 80)
    print("ADVANCED EXAMPLES")
    print("=" * 80)
    
    # 23. Analyze specific year with multiple metrics
    print("\n23. Comprehensive Year Analysis (2023):")
    year_2023 = reader.get_by_year(2023)
    if len(year_2023) > 0:
        year_analyzer = StockDataAnalyzer(year_2023)
        
        print(f"   Total Trading Days: {len(year_2023)}")
        print(f"   Average Close: {year_analyzer.average('Close'):.2f}")
        print(f"   Median Close: {year_analyzer.median('Close'):.2f}")
        print(f"   Std Deviation: {year_analyzer.std_dev('Close'):.2f}")
        
        max_info = year_analyzer.max_value('Close')
        min_info = year_analyzer.min_value('Close')
        print(f"   Highest: {max_info['value']:.2f} on {max_info['date']}")
        print(f"   Lowest: {min_info['value']:.2f} on {min_info['date']}")
        print(f"   Year Range: {max_info['value'] - min_info['value']:.2f}")
    
    # 24. Quarter-over-quarter comparison
    print("\n24. Quarter-over-Quarter Comparison (2023):")
    try:
        for q in [1, 2, 3, 4]:
            q_data = reader.get_by_quarter(2023, q)
            if len(q_data) > 0:
                q_analyzer = StockDataAnalyzer(q_data)
                avg_close = q_analyzer.average('Close')
                print(f"   Q{q} 2023: Avg Close = {avg_close:.2f}, Records = {len(q_data)}")
    except Exception as e:
        print(f"   Note: {e}")
    
    # 25. Month-by-month analysis
    print("\n25. Month-by-Month Analysis (First 3 months of 2024):")
    try:
        for month in [1, 2, 3]:
            month_data = reader.get_by_month(2024, month)
            if len(month_data) > 0:
                month_analyzer = StockDataAnalyzer(month_data)
                avg_close = month_analyzer.average('Close')
                max_info = month_analyzer.max_value('Close')
                print(f"   Month {month}: Avg = {avg_close:.2f}, Max = {max_info['value']:.2f}")
    except Exception as e:
        print(f"   Note: {e}")
    
    print("\n" + "=" * 80)
    print("Examples completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
