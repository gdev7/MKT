#!/usr/bin/env python3
"""
View shareholding pattern data from enriched metadata.

Usage:
    python src/scripts/view_shareholding.py SYMBOL [--format table|chart]
    
Examples:
    python src/scripts/view_shareholding.py LTF
    python src/scripts/view_shareholding.py RELIANCE --format table
"""

import json
import sys
import argparse
from tabulate import tabulate
from collections import defaultdict

METADATA_FILE = 'data/metadata/stocks_metadata.json'


def view_shareholding_pattern(symbol, format_type='table'):
    """
    Display shareholding pattern for a stock
    
    Args:
        symbol: Stock symbol
        format_type: Display format ('table' or 'chart')
    """
    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)
    
    if symbol not in metadata:
        print(f"Error: Symbol '{symbol}' not found in metadata")
        return
    
    stock = metadata[symbol]
    company_name = stock.get('NAME OF COMPANY', symbol)
    
    if 'SHAREHOLDING_PATTERN' not in stock:
        print(f"\nNo shareholding pattern data for {symbol} - {company_name}")
        return
    
    shareholding = stock['SHAREHOLDING_PATTERN']
    
    print(f"\n{'='*100}")
    print(f"{symbol} - {company_name}")
    print(f"SHAREHOLDING PATTERN (Quarterly)")
    print(f"{'='*100}\n")
    
    # Organize data by quarter
    by_quarter = defaultdict(dict)
    
    for record in shareholding:
        quarter = record.get('quarter')
        shareholder_type = record.get('type')
        percentage = record.get('percentage')
        
        # Skip 'No. of Shareholders'
        if shareholder_type != 'No. of Shareholders':
            by_quarter[quarter][shareholder_type] = percentage
    
    if format_type == 'table':
        # Table format - quarters as rows, types as columns
        quarters = sorted(by_quarter.keys(), reverse=True)  # Most recent first
        
        # Get all shareholder types
        all_types = set()
        for quarter_data in by_quarter.values():
            all_types.update(quarter_data.keys())
        
        types = sorted(all_types)
        
        # Build table
        headers = ['Quarter'] + types
        rows = []
        
        for quarter in quarters:
            row = [quarter]
            for shareholder_type in types:
                value = by_quarter[quarter].get(shareholder_type, '-')
                row.append(value)
            rows.append(row)
        
        print(tabulate(rows, headers=headers, tablefmt='grid', stralign='right'))
        
        # Show trends
        if len(quarters) >= 2:
            print(f"\n📊 TRENDS (Latest vs Previous Quarter):")
            print("-" * 100)
            
            latest = quarters[0]
            previous = quarters[1]
            
            for shareholder_type in types:
                latest_val = by_quarter[latest].get(shareholder_type)
                prev_val = by_quarter[previous].get(shareholder_type)
                
                if latest_val and prev_val:
                    try:
                        latest_num = float(latest_val.replace('%', '').strip())
                        prev_num = float(prev_val.replace('%', '').strip())
                        change = latest_num - prev_num
                        
                        arrow = '↑' if change > 0 else '↓' if change < 0 else '→'
                        
                        print(f"  {shareholder_type:<25} {prev_val:>8} → {latest_val:>8}  {arrow} {change:+.2f}%")
                    except:
                        pass
    
    else:  # chart format
        # Simple text-based bar chart
        print("Shareholding Distribution (Latest Quarter):\n")
        
        latest_quarter = max(by_quarter.keys())
        data = by_quarter[latest_quarter]
        
        print(f"Quarter: {latest_quarter}\n")
        
        for shareholder_type, percentage in sorted(data.items()):
            try:
                pct = float(percentage.replace('%', '').strip())
                bar_length = int(pct / 2)  # Scale to fit
                bar = '█' * bar_length
                print(f"{shareholder_type:<25} {percentage:>8}  {bar}")
            except:
                print(f"{shareholder_type:<25} {percentage:>8}")
    
    print(f"\n{'='*100}\n")


def compare_stocks(symbols):
    """
    Compare shareholding patterns across multiple stocks
    
    Args:
        symbols: List of stock symbols to compare
    """
    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)
    
    print(f"\n{'='*100}")
    print("SHAREHOLDING PATTERN COMPARISON")
    print(f"{'='*100}\n")
    
    # Get latest quarter data for each stock
    comparison_data = []
    
    for symbol in symbols:
        if symbol not in metadata:
            print(f"Warning: {symbol} not found in metadata")
            continue
        
        stock = metadata[symbol]
        
        if 'SHAREHOLDING_PATTERN' not in stock:
            print(f"Warning: {symbol} has no shareholding data")
            continue
        
        shareholding = stock['SHAREHOLDING_PATTERN']
        
        # Get latest quarter
        by_quarter = defaultdict(dict)
        for record in shareholding:
            quarter = record.get('quarter')
            shareholder_type = record.get('type')
            percentage = record.get('percentage')
            
            if shareholder_type != 'No. of Shareholders':
                by_quarter[quarter][shareholder_type] = percentage
        
        latest_quarter = max(by_quarter.keys())
        data = by_quarter[latest_quarter]
        
        row = [symbol, stock.get('NAME OF COMPANY', symbol)[:30], latest_quarter]
        
        for shareholder_type in ['Promoters+', 'FIIs+', 'DIIs+', 'Public+']:
            row.append(data.get(shareholder_type, '-'))
        
        comparison_data.append(row)
    
    headers = ['Symbol', 'Company', 'Quarter', 'Promoters', 'FIIs', 'DIIs', 'Public']
    print(tabulate(comparison_data, headers=headers, tablefmt='grid'))
    
    print(f"\n{'='*100}\n")


def main():
    parser = argparse.ArgumentParser(description='View shareholding pattern data')
    parser.add_argument('symbols', nargs='+', help='Stock symbol(s) to view')
    parser.add_argument('--format', choices=['table', 'chart'], default='table',
                       help='Display format (default: table)')
    parser.add_argument('--compare', action='store_true',
                       help='Compare multiple stocks (provide multiple symbols)')
    
    args = parser.parse_args()
    
    if args.compare or len(args.symbols) > 1:
        compare_stocks(args.symbols)
    else:
        view_shareholding_pattern(args.symbols[0], args.format)


if __name__ == '__main__':
    main()
