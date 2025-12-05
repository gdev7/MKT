"""
View time-series data (Quarterly Results, Shareholding Pattern).

Usage:
    python src/scripts/view_timeseries.py RELIANCE
    python src/scripts/view_timeseries.py BAJAJ-AUTO --type quarterly
    python src/scripts/view_timeseries.py INFY --type shareholding
"""
import json
import argparse
from pathlib import Path
from tabulate import tabulate

METADATA_FILE = Path("data/metadata/stocks_metadata.json")


def view_quarterly_results(symbol: str, stock: dict):
    """Display quarterly results in tabular format."""
    if 'QUARTERLY_RESULTS' not in stock or not stock['QUARTERLY_RESULTS']:
        print(f"\n{symbol}: No quarterly results data available")
        return
    
    results = stock['QUARTERLY_RESULTS']
    
    print(f"\n{'='*100}")
    print(f"{symbol} - Quarterly Results")
    print(f"{'='*100}")
    print(f"Total quarters: {len(results)}\n")
    
    # Prepare table data
    headers = ['Quarter', 'Sales', 'Operating Profit', 'OPM', 'Net Profit', 'NPM', 'EPS']
    rows = []
    
    for q in results:
        row = [
            q.get('quarter', 'N/A'),
            q.get('sales', '-'),
            q.get('operating_profit', '-'),
            q.get('opm', '-'),
            q.get('net_profit', '-'),
            q.get('npm', '-'),
            q.get('eps', '-')
        ]
        rows.append(row)
    
    print(tabulate(rows, headers=headers, tablefmt='grid'))
    
    # Show full details for latest quarter
    if results:
        print(f"\nLatest Quarter Details ({results[0].get('quarter', 'N/A')}):")
        print('-' * 50)
        for key, value in results[0].items():
            if key != 'quarter':
                print(f"  {key:25} {value}")


def view_shareholding_pattern(symbol: str, stock: dict):
    """Display shareholding pattern in tabular format."""
    if 'SHAREHOLDING_PATTERN' not in stock or not stock['SHAREHOLDING_PATTERN']:
        print(f"\n{symbol}: No shareholding pattern data available")
        return
    
    pattern = stock['SHAREHOLDING_PATTERN']
    
    print(f"\n{'='*100}")
    print(f"{symbol} - Shareholding Pattern")
    print(f"{'='*100}")
    print(f"Total records: {len(pattern)}\n")
    
    # Group by quarter
    quarters = {}
    for record in pattern:
        quarter = record['quarter']
        if quarter not in quarters:
            quarters[quarter] = {}
        quarters[quarter][record['type']] = record['percentage']
    
    # Prepare table
    shareholder_types = list(set(r['type'] for r in pattern))
    headers = ['Quarter'] + shareholder_types
    rows = []
    
    for quarter in sorted(quarters.keys(), reverse=True):
        row = [quarter]
        for sh_type in shareholder_types:
            row.append(quarters[quarter].get(sh_type, '-') + '%' if quarters[quarter].get(sh_type) else '-')
        rows.append(row)
    
    print(tabulate(rows, headers=headers, tablefmt='grid'))


def view_all_timeseries(symbol: str):
    """View all time-series data for a stock."""
    with open(METADATA_FILE, 'r') as f:
        data = json.load(f)
    
    if symbol not in data:
        print(f"Stock {symbol} not found in metadata")
        return
    
    stock = data[symbol]
    
    # Check what time-series data is available
    has_quarterly = 'QUARTERLY_RESULTS' in stock and stock['QUARTERLY_RESULTS']
    has_shareholding = 'SHAREHOLDING_PATTERN' in stock and stock['SHAREHOLDING_PATTERN']
    
    if not has_quarterly and not has_shareholding:
        print(f"\n{symbol}: No time-series data available")
        return
    
    print(f"\n{'='*100}")
    print(f"{symbol} - Time-Series Data Overview")
    print(f"{'='*100}")
    print(f"Company: {stock.get('NAME', 'N/A')}")
    print(f"Sector: {stock.get('BROAD_SECTOR', 'N/A')} > {stock.get('SUB_SECTOR', 'N/A')}")
    print(f"Last Updated: {stock.get('LAST_UPDATED', 'N/A')}")
    
    if has_quarterly:
        view_quarterly_results(symbol, stock)
    
    if has_shareholding:
        view_shareholding_pattern(symbol, stock)


def main():
    parser = argparse.ArgumentParser(description="View time-series data for stocks")
    parser.add_argument('symbol', help='Stock symbol (e.g., RELIANCE)')
    parser.add_argument('--type', choices=['quarterly', 'shareholding', 'all'], 
                       default='all', help='Type of time-series data to view')
    args = parser.parse_args()
    
    with open(METADATA_FILE, 'r') as f:
        data = json.load(f)
    
    if args.symbol not in data:
        print(f"Stock {args.symbol} not found in metadata")
        return
    
    stock = data[args.symbol]
    
    if args.type == 'quarterly':
        view_quarterly_results(args.symbol, stock)
    elif args.type == 'shareholding':
        view_shareholding_pattern(args.symbol, stock)
    else:
        view_all_timeseries(args.symbol)


if __name__ == "__main__":
    main()
