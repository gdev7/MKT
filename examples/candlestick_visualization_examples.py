"""
Candlestick Visualization Examples

This script demonstrates all features of the CandlestickVisualizer class.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_fetch.stock_data_reader import StockDataReader
from src.visualization.candlestick_visualizer import CandlestickVisualizer


def main():
    """Demonstrate all candlestick visualization features."""
    
    print("=" * 80)
    print("CANDLESTICK VISUALIZATION EXAMPLES")
    print("=" * 80)
    
    # Load stock data
    csv_path = Path(__file__).parent.parent / 'data' / 'raw' / '3MINDIA.csv'
    reader = StockDataReader(csv_path)
    
    print(f"\nLoaded stock data: {reader.symbol}")
    print(f"Total records: {len(reader.data)}")
    
    # Get recent data for better visualization
    data_2024 = reader.get_by_year(2024)
    print(f"Using 2024 data: {len(data_2024)} records")
    
    # Initialize visualizer
    visualizer = CandlestickVisualizer(data_2024, symbol='3MINDIA')
    print(f"\nInitialized: {visualizer}")
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / 'output' / 'charts'
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nCharts will be saved to: {output_dir}")
    
    # Example 1: Daily candlestick chart
    print("\n" + "=" * 80)
    print("1. Daily Candlestick Chart")
    print("=" * 80)
    
    fig_daily = visualizer.plot_daily(
        title='3MINDIA - Daily Chart (2024)',
        show_volume=True,
        moving_averages=[20, 50],
        show_rangeslider=True
    )
    
    output_file = output_dir / 'daily_candlestick.html'
    visualizer.save_chart(fig_daily, str(output_file))
    print(f"✓ Daily chart created with 20 & 50-day moving averages")
    
    # Example 2: Weekly candlestick chart
    print("\n" + "=" * 80)
    print("2. Weekly Candlestick Chart")
    print("=" * 80)
    
    fig_weekly = visualizer.plot_weekly(
        title='3MINDIA - Weekly Chart (2024)',
        show_volume=True,
        moving_averages=[10, 20],
        height=900
    )
    
    output_file = output_dir / 'weekly_candlestick.html'
    visualizer.save_chart(fig_weekly, str(output_file))
    print(f"✓ Weekly chart created with 10 & 20-week moving averages")
    
    # Example 3: Monthly candlestick chart
    print("\n" + "=" * 80)
    print("3. Monthly Candlestick Chart")
    print("=" * 80)
    
    # Get more data for monthly view
    data_multi_year = reader.get_by_year([2022, 2023, 2024])
    visualizer_multi = CandlestickVisualizer(data_multi_year, symbol='3MINDIA')
    
    fig_monthly = visualizer_multi.plot_monthly(
        title='3MINDIA - Monthly Chart (2022-2024)',
        show_volume=True,
        moving_averages=[6, 12],
        height=900
    )
    
    output_file = output_dir / 'monthly_candlestick.html'
    visualizer_multi.save_chart(fig_monthly, str(output_file))
    print(f"✓ Monthly chart created with 6 & 12-month moving averages")
    
    # Example 4: Quarterly candlestick chart
    print("\n" + "=" * 80)
    print("4. Quarterly Candlestick Chart")
    print("=" * 80)
    
    # Get 5 years of data for quarterly view
    data_5y = reader.get_date_range('2020-01-01', '2024-12-31')
    visualizer_5y = CandlestickVisualizer(data_5y, symbol='3MINDIA')
    
    fig_quarterly = visualizer_5y.plot_quarterly(
        title='3MINDIA - Quarterly Chart (2020-2024)',
        show_volume=True,
        moving_averages=[4, 8],
        height=900
    )
    
    output_file = output_dir / 'quarterly_candlestick.html'
    visualizer_5y.save_chart(fig_quarterly, str(output_file))
    print(f"✓ Quarterly chart created with 4 & 8-quarter moving averages")
    
    # Example 5: Yearly candlestick chart
    print("\n" + "=" * 80)
    print("5. Yearly Candlestick Chart")
    print("=" * 80)
    
    # Get all available data for yearly view
    data_all = reader.get_columns()
    visualizer_all = CandlestickVisualizer(data_all, symbol='3MINDIA')
    
    fig_yearly = visualizer_all.plot_yearly(
        title='3MINDIA - Yearly Chart (All Time)',
        show_volume=True,
        moving_averages=[3, 5],
        height=900
    )
    
    output_file = output_dir / 'yearly_candlestick.html'
    visualizer_all.save_chart(fig_yearly, str(output_file))
    print(f"✓ Yearly chart created with 3 & 5-year moving averages")
    
    # Example 6: Chart without volume
    print("\n" + "=" * 80)
    print("6. Chart Without Volume Overlay")
    print("=" * 80)
    
    fig_no_volume = visualizer.plot_daily(
        title='3MINDIA - Daily Chart (No Volume)',
        show_volume=False,
        moving_averages=[20, 50, 200],
        show_rangeslider=True,
        height=700
    )
    
    output_file = output_dir / 'daily_no_volume.html'
    visualizer.save_chart(fig_no_volume, str(output_file))
    print(f"✓ Chart created without volume overlay")
    
    # Example 7: Classic color scheme
    print("\n" + "=" * 80)
    print("7. Classic Color Scheme (Black & White)")
    print("=" * 80)
    
    fig_classic = visualizer.plot_weekly(
        title='3MINDIA - Weekly Chart (Classic Colors)',
        show_volume=True,
        moving_averages=[10, 20],
        color_scheme='classic',
        height=900
    )
    
    output_file = output_dir / 'weekly_classic_colors.html'
    visualizer.save_chart(fig_classic, str(output_file))
    print(f"✓ Chart created with classic black & white color scheme")
    
    # Example 8: Multi-timeframe comparison
    print("\n" + "=" * 80)
    print("8. Multi-Timeframe Comparison Chart")
    print("=" * 80)
    
    fig_comparison = visualizer_multi.create_comparison_chart(
        timeframes=['D', 'W', 'M'],
        moving_averages=[20, 50],
        height=1400
    )
    
    output_file = output_dir / 'multi_timeframe_comparison.html'
    visualizer_multi.save_chart(fig_comparison, str(output_file))
    print(f"✓ Multi-timeframe comparison chart created (Daily, Weekly, Monthly)")
    
    # Example 9: Custom date range
    print("\n" + "=" * 80)
    print("9. Custom Date Range Chart")
    print("=" * 80)
    
    # Get Q1 2024 data
    q1_data = reader.get_by_quarter(2024, 1)
    visualizer_q1 = CandlestickVisualizer(q1_data, symbol='3MINDIA')
    
    fig_q1 = visualizer_q1.plot_daily(
        title='3MINDIA - Q1 2024 Daily Chart',
        show_volume=True,
        moving_averages=[10, 20],
        height=900
    )
    
    output_file = output_dir / 'q1_2024_daily.html'
    visualizer_q1.save_chart(fig_q1, str(output_file))
    print(f"✓ Q1 2024 daily chart created")
    
    # Example 10: Save as static image (PNG)
    print("\n" + "=" * 80)
    print("10. Save Chart as Static Image (PNG)")
    print("=" * 80)
    
    try:
        output_file = output_dir / 'weekly_chart.png'
        visualizer.save_chart(
            fig_weekly,
            str(output_file),
            format='png',
            width=1920,
            height=1080
        )
        print(f"✓ Chart saved as PNG image")
    except Exception as e:
        print(f"Note: PNG export requires kaleido: {e}")
    
    # Example 11: Using timeframe aliases
    print("\n" + "=" * 80)
    print("11. Using Timeframe Aliases")
    print("=" * 80)
    
    # All these are equivalent
    fig_w1 = visualizer.plot_candlestick(timeframe='week', show_volume=False, height=600)
    fig_w2 = visualizer.plot_candlestick(timeframe='W', show_volume=False, height=600)
    fig_w3 = visualizer.plot_candlestick(timeframe='weekly', show_volume=False, height=600)
    
    print(f"✓ Timeframe aliases work: 'week', 'W', 'weekly' all create weekly charts")
    
    # Example 12: Recent data analysis
    print("\n" + "=" * 80)
    print("12. Recent 90-Day Analysis")
    print("=" * 80)
    
    # Get last 90 days
    recent_data = reader.get_lookback('2024-12-31', days=90)
    visualizer_recent = CandlestickVisualizer(recent_data, symbol='3MINDIA')
    
    fig_recent = visualizer_recent.plot_daily(
        title='3MINDIA - Last 90 Days',
        show_volume=True,
        moving_averages=[10, 20, 50],
        height=900
    )
    
    output_file = output_dir / 'recent_90_days.html'
    visualizer_recent.save_chart(fig_recent, str(output_file))
    print(f"✓ Recent 90-day chart created")
    
    print("\n" + "=" * 80)
    print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print(f"\nAll charts have been saved to: {output_dir}")
    print("\nTo view the charts:")
    print("1. Open any .html file in your web browser")
    print("2. Use mouse to zoom, pan, and hover over data points")
    print("3. Click legend items to show/hide traces")
    print("4. Double-click to reset zoom")
    
    print("\nInteractive Features:")
    print("- Zoom: Click and drag on the chart")
    print("- Pan: Hold Shift and drag")
    print("- Hover: Move mouse over candles for details")
    print("- Reset: Double-click anywhere on the chart")
    print("- Toggle: Click legend items to show/hide")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
