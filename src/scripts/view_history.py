"""
View historical changes for stock metrics.

Usage:
    python src/scripts/view_history.py RELIANCE
    python src/scripts/view_history.py BAJAJ-AUTO --field MARKET_CAP
    python src/scripts/view_history.py --all --field PE_RATIO
"""
import json
import argparse
from pathlib import Path
from datetime import datetime

METADATA_FILE = Path("data/metadata/stocks_metadata.json")


def view_stock_history(symbol: str, field: str = None):
    """View history for a specific stock."""
    with open(METADATA_FILE, 'r') as f:
        data = json.load(f)
    
    if symbol not in data:
        print(f"Stock {symbol} not found in metadata")
        return
    
    stock = data[symbol]
    
    if 'HISTORY' not in stock or not stock['HISTORY']:
        print(f"\n{symbol}: No historical changes recorded yet")
        return
    
    print(f"\n{'='*80}")
    print(f"{symbol} - Historical Changes")
    print(f"{'='*80}")
    
    history = stock['HISTORY']
    
    # If specific field requested
    if field:
        if field not in history:
            print(f"\nNo history for field: {field}")
            print(f"Available fields: {list(history.keys())}")
            return
        
        print(f"\n{field}:")
        print(f"  Current Value: {stock.get(field, 'N/A')}")
        print(f"\n  Historical Changes:")
        print(f"  {'Date':<12} {'Old Value':<15} {'New Value':<15} {'Change':<12} {'% Change':<10}")
        print(f"  {'-'*70}")
        
        for record in history[field]:
            print(f"  {record['date']:<12} {str(record['old_value']):<15} {str(record['new_value']):<15} "
                  f"{record['change']:<12.2f} {record['pct_change']:<10.2f}%")
    
    else:
        # Show all fields
        for field_name, records in history.items():
            print(f"\n{field_name}:")
            print(f"  Current Value: {stock.get(field_name, 'N/A')}")
            print(f"\n  {'Date':<12} {'Old Value':<15} {'New Value':<15} {'Change':<12} {'% Change':<10}")
            print(f"  {'-'*70}")
            
            for record in records:
                print(f"  {record['date']:<12} {str(record['old_value']):<15} {str(record['new_value']):<15} "
                      f"{record['change']:<12.2f} {record['pct_change']:<10.2f}%")


def view_all_changes(field: str = None):
    """View all stocks that have changes in a specific field."""
    with open(METADATA_FILE, 'r') as f:
        data = json.load(f)
    
    stocks_with_changes = []
    
    for symbol, stock in data.items():
        if 'HISTORY' not in stock or not stock['HISTORY']:
            continue
        
        if field:
            if field in stock['HISTORY'] and stock['HISTORY'][field]:
                # Get latest change
                latest = stock['HISTORY'][field][-1]
                stocks_with_changes.append({
                    'symbol': symbol,
                    'date': latest['date'],
                    'old_value': latest['old_value'],
                    'new_value': latest['new_value'],
                    'change': latest['change'],
                    'pct_change': latest['pct_change']
                })
        else:
            stocks_with_changes.append({
                'symbol': symbol,
                'fields': list(stock['HISTORY'].keys()),
                'total_changes': sum(len(records) for records in stock['HISTORY'].values())
            })
    
    if not stocks_with_changes:
        print("\nNo historical changes found")
        return
    
    print(f"\n{'='*80}")
    if field:
        print(f"All Stocks with {field} Changes (Latest)")
        print(f"{'='*80}")
        print(f"{'Symbol':<15} {'Date':<12} {'Old Value':<15} {'New Value':<15} {'Change':<12} {'% Change':<10}")
        print(f"{'-'*80}")
        
        # Sort by percentage change
        stocks_with_changes.sort(key=lambda x: abs(x['pct_change']), reverse=True)
        
        for item in stocks_with_changes:
            print(f"{item['symbol']:<15} {item['date']:<12} {str(item['old_value']):<15} "
                  f"{str(item['new_value']):<15} {item['change']:<12.2f} {item['pct_change']:<10.2f}%")
    else:
        print(f"All Stocks with Historical Changes")
        print(f"{'='*80}")
        print(f"{'Symbol':<15} {'Fields Tracked':<40} {'Total Changes':<15}")
        print(f"{'-'*80}")
        
        for item in stocks_with_changes:
            fields_str = ', '.join(item['fields'][:3])
            if len(item['fields']) > 3:
                fields_str += f"... (+{len(item['fields'])-3} more)"
            print(f"{item['symbol']:<15} {fields_str:<40} {item['total_changes']:<15}")
    
    print(f"\nTotal stocks with changes: {len(stocks_with_changes)}")


def main():
    parser = argparse.ArgumentParser(description="View historical changes for stock metrics")
    parser.add_argument('symbol', nargs='?', help='Stock symbol (e.g., RELIANCE)')
    parser.add_argument('--field', help='Specific field to view (e.g., MARKET_CAP, PE_RATIO)')
    parser.add_argument('--all', action='store_true', help='View all stocks with changes')
    args = parser.parse_args()
    
    if args.all:
        view_all_changes(args.field)
    elif args.symbol:
        view_stock_history(args.symbol, args.field)
    else:
        print("Please provide a stock symbol or use --all")
        parser.print_help()


if __name__ == "__main__":
    main()
